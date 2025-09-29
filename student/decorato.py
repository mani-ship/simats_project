from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

def student_login_required(view_func):
    @never_cache  # prevents browser caching
    def wrapper(request, *args, **kwargs):
        if not request.session.get("student_id"):
            # Redirect to landing page if not logged in
            return redirect("login_options")
        return view_func(request, *args, **kwargs)
    return wrapper
