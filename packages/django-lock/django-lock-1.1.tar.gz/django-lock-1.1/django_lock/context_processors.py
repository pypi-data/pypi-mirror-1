def lock_previewing(request):
    if getattr(request, 'lock_previewing', None):
        return {'lock_previewing': True}
    return {}