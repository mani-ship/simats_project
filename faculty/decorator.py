from django.shortcuts import redirect
from django.contrib import messages

def faculty_login_required(view_func):
    """
    Decorator to allow only logged-in faculty to access the view.
    Redirects to faculty login if session not found.
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get('faculty_id'):
            messages.error(request, "Please login first to access this page.")
            return redirect('faculty_login')
        return view_func(request, *args, **kwargs)
    return wrapper
