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

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_str
from django.views.generic.simple import direct_to_template as d2t

from django_lock import SESSION_KEY, SESSION_USER, PREVIEW_PASSWORD_KEY

class NotEntered:
    pass
NOT_ENTERED = NotEntered()

def lock(preview_password=NOT_ENTERED, preview_auth=NOT_ENTERED,
         until_date=NOT_ENTERED, after_date=NOT_ENTERED):
    if until_date == NOT_ENTERED:
        until_date = getattr(settings, 'LOCK_UNTIL_DATE', None)
    if after_date == NOT_ENTERED:
        after_date = getattr(settings, 'LOCK_AFTER_DATE', None)
    if preview_password == NOT_ENTERED:
        preview_password = getattr(settings, 'LOCK_PREVIEW_PASSWORD', None)
    if preview_password and not isinstance(preview_password, (tuple, list)):
        preview_password = (preview_password,)
    if preview_auth == NOT_ENTERED:
        preview_auth = getattr(settings, 'LOCK_PREVIEW_AUTH', None)
    def protect(func):
        def dec(request, *args, **kwargs):
            c = {}
            if request.method == 'POST':
                if preview_password and PREVIEW_PASSWORD_KEY in request.POST:
                    password = request.POST.get(PREVIEW_PASSWORD_KEY)
                    request.session[SESSION_KEY] = password
                    return HttpResponseRedirect(request.get_full_path())
                if preview_auth:
                    user = authenticate(**dict([(smart_str(k), v) for k, v in
                                                request.POST.items()]))
                    if user:
                        request.session[SESSION_USER] = user
                        return HttpResponseRedirect(request.get_full_path())
            c = {}
            if preview_password:
                c['accepts_password'] = True
                c['preview_password_key'] = PREVIEW_PASSWORD_KEY
            if preview_auth:
                c['accepts_credentials'] = True
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
                if (preview_password and request.session.get(SESSION_KEY) in
                                                            preview_password):
                    request.lock_previewing = True
                    locked = False
                elif preview_auth:
                    user = request.session.get(SESSION_USER)
                    if user:
                        # Ensure the user is still a user in the database.
                        try:
                            user = user._default_manager.get(pk=user.pk)
                        except user.DoesNotExist:
                            user = None
                    if user and user.is_active and (not preview_auth == 'staff'
                                                    or user.is_staff):
                        request.lock_previewing = True
                        locked = False
            if locked:
                return d2t(request, 'lock/lock.htm', c)
            return func(request, *args, **kwargs)
        return wraps(func)(dec)
    return protect
