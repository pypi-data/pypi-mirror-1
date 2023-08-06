# -*- coding: utf-8 -*-
import threading
_thread_locals = threading.local()

def get_current_ip():
    "Returns current IP address."
    return getattr(_thread_locals, 'ip', None)

def get_current_user():
    "Returns current user (authenticated or anonymous)."
    return getattr(_thread_locals, 'user', None)

class ThreadIPMiddleware(object):
    def process_request(self, request):
        _thread_locals.ip = request.META['REMOTE_ADDR']
        return None

class ThreadUserMiddleware(object):
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        return None
