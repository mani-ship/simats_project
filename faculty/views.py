from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from adminui.models import Faculty
from student.models import Submission
from student.models import Problem
from faculty.decorator import faculty_login_required
from django.db.models import Q

# ----- Faculty Login -----
@never_cache
def faculty_login(request):
    list(messages.get_messages(request))

    if request.session.get('faculty_id'):
        return redirect('faculty_dashboard')

    if request.method == 'POST':
        faculty_id_input = request.POST.get('faculty_id', '').strip()
        password_input = request.POST.get('password', '').strip()

        if not faculty_id_input or not password_input:
            messages.error(request, "Please enter Faculty ID and Password.", extra_tags='faculty')
            return render(request, "faculty/login.html")

        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id_input)
            if check_password(password_input, faculty.password):
                request.session['faculty_id'] = faculty.faculty_id
                request.session['faculty_username'] = faculty.username
                return redirect('faculty_dashboard')
            else:
                messages.error(request, "Incorrect password.", extra_tags='faculty')
        except Faculty.DoesNotExist:
            messages.error(request, "Faculty ID does not exist.", extra_tags='faculty')

    response = render(request, "faculty/login.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ----- Faculty Dashboard -----
@faculty_login_required
@never_cache
def faculty_dashboard(request):
    faculty_username = request.session.get('faculty_username')
    if not faculty_username:
        return redirect('faculty_login')

    submissions_list = Submission.objects.select_related("student", "problem").order_by("-submitted_at")
    search_query = request.GET.get("search", "").strip()
    if search_query:
        submissions_list = submissions_list.filter(
            Q(student__full_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query)
        )

    paginator = Paginator(submissions_list, 7)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    response = render(request, "faculty/dashboard.html", {
        "faculty_username": faculty_username,
        "page_obj": page_obj,
        "search": search_query,
    })
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ----- Evaluate Submission -----
@faculty_login_required
@never_cache
def evaluate_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    error_message = ""

    faculty_id = request.session.get("faculty_id")
    try:
        faculty = Faculty.objects.get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Logged-in faculty not found.")
        return redirect("faculty_dashboard")

    if request.method == "POST":
        marks_input = request.POST.get("marks")
        remarks = request.POST.get("remarks", "").strip()
        try:
            marks = int(marks_input)
            if marks < 0:
                error_message = "Marks cannot be negative."
            elif marks > submission.problem.total_marks:
                error_message = f"Marks cannot exceed {submission.problem.total_marks}."
            else:
                submission.faculty_marks = marks
                submission.faculty_remarks = remarks
                submission.faculty = faculty
                submission.save()
                return redirect("faculty_dashboard")
        except (ValueError, TypeError):
            error_message = "Please enter a valid number for marks."

    response = render(request, "faculty/evaluate_submission.html", {
        "submission": submission,
        "error_message": error_message
    })
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ----- Faculty Logout -----
@faculty_login_required
@never_cache
def faculty_logout(request):
    request.session.flush()
    list(messages.get_messages(request))
    return redirect("login_options")
