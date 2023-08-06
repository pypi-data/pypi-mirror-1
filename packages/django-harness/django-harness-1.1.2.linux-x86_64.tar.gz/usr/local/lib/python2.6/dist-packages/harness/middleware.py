# -*- coding: utf-8 -*-
import threading
_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class ThreadUserMiddleware(object):
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        return None
