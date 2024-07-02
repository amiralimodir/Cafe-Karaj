from django.http import HttpResponseForbidden

def admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view_func
