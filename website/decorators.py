from django.http import HttpResponseForbidden
from .models import Admin

def admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(username=request.user.username).exists():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view_func