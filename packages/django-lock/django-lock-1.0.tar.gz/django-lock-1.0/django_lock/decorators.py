"""
Password protection decorator

Set up the decorator at the top of your URLconf like so::

    from django_lock.decorators import lock
    protect = lock(preview_password='******')

    @protect
    def my_view(request):
        ...
"""

from datetime import datetime
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

from django.views.generic.simple import direct_to_template as d2t
from django.conf import settings
from django.http import HttpResponseRedirect

from django_lock import SESSION_KEY, PREVIEW_PASSWORD_KEY

class NotEntered:
    pass
NOT_ENTERED = NotEntered()

def lock(preview_password=NOT_ENTERED, until_date=NOT_ENTERED, after_date=NOT_ENTERED):
    if until_date == NOT_ENTERED:
        until_date = getattr(settings, 'LOCK_UNTIL_DATE', None)
    if after_date == NOT_ENTERED:
        after_date = getattr(settings, 'LOCK_AFTER_DATE', None)
    if preview_password == NOT_ENTERED:
        preview_password = getattr(settings, 'LOCK_PREVIEW_PASSWORD', None)
    if preview_password and not isinstance(preview_password, (tuple, list)):
        preview_password = (preview_password,)
    def protect(func):
        def dec(request, *args, **kwargs):
            password = request.session.get(SESSION_KEY)
            if request.method == 'POST' and PREVIEW_PASSWORD_KEY in request.POST:
                password = request.POST.get(PREVIEW_PASSWORD_KEY)
                request.session[SESSION_KEY] = password
                return HttpResponseRedirect(request.get_full_path())
            c = {
                'accepts_password': bool(preview_password),
                'preview_password_key': PREVIEW_PASSWORD_KEY,
            }
            now = datetime.now()
            if until_date and now < until_date:
                c['until_date'] = until_date
                locked = True
            elif after_date and now > after_date:
                c['after_date'] = after_date
                locked = True
            elif after_date or until_date:
                # A date was provided and it passed the previous tests so no
                # lock is required.
                locked = False
            else:
                locked = True
            if locked:
                if preview_password and password in preview_password:
                    request.lock_previewing = True
                else:
                    return d2t(request, 'lock/lock.htm', c)
            return func(request, *args, **kwargs)
        return wraps(func)(dec)
    return protect
