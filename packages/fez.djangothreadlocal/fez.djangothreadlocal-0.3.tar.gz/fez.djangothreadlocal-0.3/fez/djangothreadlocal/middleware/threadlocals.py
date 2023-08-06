from django.core import signals

# based on: http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser
# threadlocals middleware
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
def get_current_user():
    return getattr(_thread_locals, 'user', None)

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        
# Hook up a signal handler to django's request_finished signal
# to clear out the user from the threadlocal. This is useful
# for testing.
def clear_user(signal, sender, **kwargs):
    if hasattr(_thread_locals, 'user'):
        del _thread_locals.user
signals.request_finished.connect(clear_user)
