from django.http import HttpResponseRedirect

from django_lock import SESSION_KEY

def logout(request, next_page):
    try:
        del request.session[SESSION_KEY]
    except KeyError:
        pass
    return HttpResponseRedirect(next_page)
