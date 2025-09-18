from django.shortcuts import redirect

def faculty_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("faculty_id"):
            return redirect("faculty_login")  # your faculty login url name
        return view_func(request, *args, **kwargs)
    return wrapper
