try:
    from functools import update_wrapper, wraps
except ImportError:
    from django.utils.functional import update_wrapper, wraps  # Python 2.3, 2.4 fallback.

from django.http import HttpResponseForbidden

def has_app_perm(app, view_func):
    """Returns 403 response if the request.user does not have permissions to for
    the app.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.has_module_perms(app):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('You lack the permission to %s ' \
                                     '%s' % (request.method, request.path))
    return wraps(view_func)(_wrapped_view)

