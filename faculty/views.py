from django.shortcuts import render, redirect
from django.contrib import messages
from adminui.models import Faculty
from student.models import Problem, Submission  # import student models



from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from adminui.models import Faculty

def faculty_login(request):
    # If already logged in → go to dashboard
    if request.session.get('faculty_id'):
        return redirect('faculty_dashboard')

    if request.method == 'POST':
        faculty_id_input = request.POST.get('faculty_id', '').strip()
        password_input = request.POST.get('password', '').strip()

        if not faculty_id_input or not password_input:
            messages.error(request, "Please enter Faculty ID and Password.")
            return render(request, "faculty/login.html")

        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id_input)
            if check_password(password_input, faculty.password):  # ✅ hashed password check
                request.session['faculty_id'] = faculty.faculty_id
                request.session['faculty_username'] = faculty.username
                return redirect('faculty_dashboard')
            else:
                messages.error(request, "Incorrect password.")
        except Faculty.DoesNotExist:
            messages.error(request, "Faculty ID does not exist.")

    return render(request, "faculty/login.html")





from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.db.models import Q
from .decorators import faculty_login_required
from student.models import Submission

from django.db.models import Q

@faculty_login_required
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

    return render(request, "faculty/dashboard.html", {
        "faculty_username": faculty_username,
        "page_obj": page_obj,
        "search": search_query,  # pass to template
    })








from django.shortcuts import render, redirect, get_object_or_404
from student.models import Submission


from django.shortcuts import render, redirect, get_object_or_404
from student.models import Submission
from .decorators import faculty_login_required

from django.shortcuts import render, redirect, get_object_or_404
from student.models import Submission
from .decorators import faculty_login_required
from adminui.models import Faculty  # import your Faculty model

@faculty_login_required
def evaluate_submission(request, submission_id):
    """
    Allows a logged-in faculty to evaluate a student's submission.
    Marks and remarks are saved, and the submission is linked to the faculty.
    """
    submission = get_object_or_404(Submission, id=submission_id)
    error_message = ""

    # Get the logged-in faculty from session
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

                # Assign the logged-in Faculty object
                submission.faculty = faculty
                submission.save()

                return redirect("faculty_dashboard")

        except (ValueError, TypeError):
            error_message = "Please enter a valid number for marks."

    return render(request, "faculty/evaluate_submission.html", {
        "submission": submission,
        "error_message": error_message
    })










def faculty_logout(request):
    request.session.flush()  # clear session
    return redirect('login_options')
