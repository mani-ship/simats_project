from django.shortcuts import redirect

def faculty_login_required(view_func):
    """
    Redirects to faculty login if not logged in.
    Does NOT add any messages to avoid cross-role message leakage.
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get("faculty_id"):
            return redirect("faculty_login")  # silent redirect
        return view_func(request, *args, **kwargs)
    return wrapper
