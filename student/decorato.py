from django.shortcuts import redirect

def student_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("student_id"):  # check if student is logged in
            return redirect("student_auth")  # redirect to login page
        return view_func(request, *args, **kwargs)
    return wrapper
