import sys
import traceback
import urllib2
import yaml
import re
import os
import threading
import logging
import time

from threadpool import WorkRequest, ThreadPool
from threadpool import NoResultsPending

from django.core.exceptions import MiddlewareNotUsed
from django.views.debug import get_safe_settings
from django.conf import settings


logger = logging.getLogger(__name__)

def _parse_environment(request):
    """Return an environment mapping for a notification from the given request."""
    env = dict( (str(k), str(v)) for (k, v) in get_safe_settings().items() )
    env.update( dict( (str(k), str(v)) for (k, v) in request.META.items() ) )
    
    env['REQUEST_URI'] = request.build_absolute_uri()
    
    return env

def _parse_traceback(trace):
    """Return the given traceback string formatted for a notification."""
    p_traceback = [ "%s:%d:in `%s'" % (filename, lineno, funcname) 
                    for filename, lineno, funcname, _
                    in traceback.extract_tb(trace) ]
    p_traceback.reverse()
    
    return p_traceback

def _parse_message(exc):
    """Return a message for a notification from the given exception."""
    return '%s: %s' % (exc.__class__.__name__, str(exc))

def _parse_request(request):
    """Return a request mapping for a notification from the given request."""
    request_get = dict( (str(k), str(v)) for (k, v) in request.GET.items() )
    request_post = dict( (str(k), str(v)) for (k, v) in request.POST.items() )
    return request_post if request_post else request_get

def _parse_session(session):
    """Return a request mapping for a notification from the given session."""
    return dict( (str(k), str(v)) for (k, v) in session.items() )


def _generate_payload(request, exc=None, trace=None, message=None, error_class=None):
    """Generate a YAML payload for a Hoptoad notification.
    
    Parameters:
    request -- A Django HTTPRequest.  This is required.
    
    Keyword parameters:
    exc -- A Python Exception object.  If this is not given the 
           mess parameter must be.
    trace -- A Python Traceback object.  This is not required.
    message -- A string representing the error message.  If this is not
               given, the exc parameter must be.
    error_class -- A string representing the error class.  If this is not
                   given the excc parameter must be.
    """
    p_message = message if message else _parse_message(exc)
    p_error_class = error_class if error_class else exc.__class__.__name__
    p_traceback = _parse_traceback(trace) if trace else []
    p_environment = _parse_environment(request)
    p_request = _parse_request(request)
    p_session = _parse_session(request.session)
    
    return yaml.dump({ 'notice': {
        'api_key':       settings.HOPTOAD_API_KEY,
        'error_class':   p_error_class,
        'error_message': p_message,
        'backtrace':     p_traceback,
        'request':       { 'url': request.build_absolute_uri(),
                           'params': p_request },
        'session':       { 'key': '', 'data': p_session },
        'environment':   p_environment,
    }}, default_flow_style=False)

def _ride_the_toad(payload, timeout):
    """Send a notification (an HTTP POST request) to Hoptoad.
    
    Parameters:
    payload -- the YAML payload for the request from _generate_payload()
    timeout -- the maximum timeout, in seconds, or None to use the default
    """
    headers = { 'Content-Type': 'application/x-yaml', 
                'Accept': 'text/xml, application/xml', }
    r = urllib2.Request('http://hoptoadapp.com/notices', payload, headers)
    try:
        if timeout:
            urllib2.urlopen(r, timeout=timeout)
        else:
            urllib2.urlopen(r)
    except urllib2.URLError:
        pass

def _exception_handler(request, exc_info):
    """Rudimentary exception handler, simply log and moves on.
    
    If there's no tuple, it means something went really wrong. Critically log
    and exit.
    """
    if not isinstance(exc_info, tuple):
        logger.critical(str(request))
        logger.critical(str(exc_info))
        sys.exit(1)
    logger.warn(
        "* Exception occured in request #%s: %s" % (request.requestID, exc_info)
    )


class Runnable(threading.Thread):
    """A daemon thread that spawns a threadpool of worker threads.
    
    Waits for queue additions through the enqueue method.
    
    # TODO: Consider using asyncore instead of a threadpool
    """
    def __init__(self, threadpool_threadcount):
        threading.Thread.__init__(self,
            name="HoptoadThreadRunner-%d" % os.getpid())
        
        self.threads = threadpool_threadcount
        self.daemon = True # daemon thread... important!
        self.pool = ThreadPool(self.threads)
    
    def enqueue(self, payload, timeout, callback=None, exc_callback=_exception_handler):
        request = WorkRequest(
            _ride_the_toad,
            args=(payload, timeout),
            callback=callback,
            exc_callback=exc_callback
        )
        
        # Put the request into the queue where the detached 'run' method will
        # poll its queue every 0.5 seconds and start working.
        self.pool.putRequest(request)
    
    def run(self):
        """Actively poll the queue for requests and process them."""
        while True:
            try:
                time.sleep(0.5) # TODO: configure for tuning
                self.pool.poll()
            except KeyboardInterrupt:
                logger.info("* Interrupted!")
                break
            except NoResultsPending:
                pass
    

class HoptoadNotifierMiddleware(object):
    def __init__(self):
        """Initialize the middleware."""
        all_settings = dir(settings)
        
        if 'HOPTOAD_API_KEY' not in all_settings or not settings.HOPTOAD_API_KEY:
            raise MiddlewareNotUsed
        
        if settings.DEBUG and \
           (not 'HOPTOAD_NOTIFY_WHILE_DEBUG' in all_settings
            or not settings.HOPTOAD_NOTIFY_WHILE_DEBUG ):
            raise MiddlewareNotUsed
        
        self.timeout = ( settings.HOPTOAD_TIMEOUT 
                         if 'HOPTOAD_TIMEOUT' in all_settings else None )
        
        self.notify_404 = ( settings.HOPTOAD_NOTIFY_404 
                            if 'HOPTOAD_NOTIFY_404' in all_settings else False )
        self.notify_403 = ( settings.HOPTOAD_NOTIFY_403 
                            if 'HOPTOAD_NOTIFY_403' in all_settings else False )
        self.ignore_agents = ( map(re.compile, settings.HOPTOAD_IGNORE_AGENTS)
                            if 'HOPTOAD_IGNORE_AGENTS' in all_settings else [] )
            
        # Creates a self.thread attribute and starts it.
        self.initialize_threadpool(all_settings)
    
    def _ignore(self, request):
        """Return True if the given request should be ignored, False otherwise."""
        ua = request.META.get('HTTP_USER_AGENT', '')
        return any(i.search(ua) for i in self.ignore_agents)
    
    def initialize_threadpool(self, all_settings):
        """Initialize an internal threadpool asynchronous POST requests.
        
        Also creates a thread attribute and starts the threadpool.
        """
        
        if 'HOPTOAD_THREAD_COUNT' in all_settings:
            threads = settings.HOPTOAD_THREAD_COUNT
        else:
            threads = 4
        
        self.thread = Runnable(threads)
        self.thread.start()
    
    def process_response(self, request, response):
        """Process a reponse object.
        
        Hoptoad will be notified of a 404 error if the response is a 404
        and 404 tracking is enabled in the settings.
        
        Hoptoad will be notified of a 403 error if the response is a 403
        and 403 tracking is enabled in the settings.
        
        Regardless of whether Hoptoad is notified, the reponse object will
        be returned unchanged.
        """
        if self._ignore(request):
            return response
        
        if self.notify_404 and response.status_code == 404:
            error_class = 'Http404'
            
            message = 'Http404: Page not found at %s' % request.build_absolute_uri()
            payload = _generate_payload(request, error_class=error_class, message=message)
            
            self.thread.enqueue(payload, self.timeout)
        
        if self.notify_403 and response.status_code == 403:
            error_class = 'Http403'
            
            message = 'Http403: Forbidden at %s' % request.build_absolute_uri()
            payload = _generate_payload(request, error_class=error_class, message=message)
            
            self.thread.enqueue(payload, self.timeout)
        
        return response
    
    def process_exception(self, request, exc):
        """Process an exception.
        
        Hoptoad will be notified of the exception and None will be
        returned so that Django's normal exception handling will then
        be used.
        """
        if self._ignore(request):
            return None
        
        excc, _, tb = sys.exc_info()
        
        payload = _generate_payload(request, exc, tb)
        self.thread.enqueue(payload, self.timeout)
        
        return None

