from django.conf import settings
from django.views.static import serve

from django_lock import decorators

protect = decorators.lock()

class LockMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # If we're in DEBUG, then let static serving get through.
        if settings.DEBUG and view_func == serve:
            return None
        passthrough = getattr(settings, 'LOCK_PASSTHROUGH', None)
        if passthrough:
            for url in passthrough:
                if request.path.startswith(url):
                    return None
        return protect(view_func)(request, *view_args, **view_kwargs)
