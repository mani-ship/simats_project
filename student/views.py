from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from .models import Student, Submission
from adminui.models import Problem
from student.decorato import student_login_required

# ----- Registration & Login -----
def register_login(request):
    # If already logged in, redirect to dashboard
    if request.session.get("student_id"):
        return redirect("student_dashboard")

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "register":
            full_name = request.POST.get("full_name")
            student_id = request.POST.get("student_id")
            password = request.POST.get("password")
            gender = request.POST.get("gender")
            year = request.POST.get("year")
            semester = request.POST.get("semester")
            department = request.POST.get("department")

            if Student.objects.filter(student_id=student_id).exists():
                messages.error(request, "Student ID already registered.")
            else:
                Student.objects.create(
                    full_name=full_name,
                    student_id=student_id,
                    password=make_password(password),
                    gender=gender,
                    year=year,
                    semester=semester,
                    department=department
                )
                messages.success(request, "Registration successful! Please login.")

        elif form_type == "login":
            student_id = request.POST.get("student_id")
            password = request.POST.get("password")
            try:
                student = Student.objects.get(student_id=student_id)
                if check_password(password, student.password):
                    request.session["student_id"] = student.id
                    request.session["student_name"] = student.full_name
                    return redirect("student_dashboard")
                else:
                    messages.error(request, "Incorrect password.")
            except Student.DoesNotExist:
                messages.error(request, "Invalid Student ID.")

    return render(request, "student/register_login.html")


# ----- Student Dashboard -----
@student_login_required
def student_dashboard(request):
    student_id = request.session.get("student_id")
    student = get_object_or_404(Student, id=student_id)

    submissions_list = Submission.objects.filter(student=student).order_by("-submitted_at")
    paginator = Paginator(submissions_list, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    submitted_problem_ids = submissions_list.values_list("problem_id", flat=True)
    next_problem = Problem.objects.exclude(id__in=submitted_problem_ids).order_by("created_at").first()

    return render(request, "student/student_dashboard.html", {
        "student": student,
        "next_problem": next_problem,
        "page_obj": page_obj,
    })


# ----- Submit Solution -----
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from student.models import Submission, Student
from adminui.models import Problem
from django.core.paginator import Paginator
from .decorato import student_login_required

@student_login_required
def submit_solution(request, problem_id):
    student_id = request.session.get("student_id")
    student = get_object_or_404(Student, id=student_id)
    problem = get_object_or_404(Problem, id=problem_id)

    error_message = ""
    success_message = ""

    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            error_message = "Please select a file to submit."
        elif Submission.objects.filter(student=student, problem=problem).exists():
            error_message = "You have already submitted this problem."
        else:
            Submission.objects.create(problem=problem, student=student, file=file)
            success_message = "Solution submitted successfully!"

    # Fetch next problem (example logic)
    next_problem = Problem.objects.exclude(submissions__student=student).first()

    # Fetch student's submissions
    submissions = Submission.objects.filter(student=student).order_by("-submitted_at")
    paginator = Paginator(submissions, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "student/student_dashboard.html", {
        "next_problem": next_problem,
        "page_obj": page_obj,
        "error_message": error_message,
        "success_message": success_message,
    })



# ----- Logout -----
@student_login_required
def student_logout(request):
    request.session.flush()  # clear all session data
    return redirect("student_auth")
