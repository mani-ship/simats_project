# student/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Student
from adminui.models import Problem
from .models import Submission

# ----- Registration & Login -----
def register_login(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # ----- Registration -----
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
                student = Student.objects.create(
                    full_name=full_name,
                    student_id=student_id,
                    password=make_password(password),  # hashed password
                    gender=gender,
                    year=year,
                    semester=semester,
                    department=department
                )
                messages.success(request, "Registration successful! Please login.")

        # ----- Login -----
        elif form_type == "login":
            student_id = request.POST.get("student_id")
            password = request.POST.get("password")

            try:
                student = Student.objects.get(student_id=student_id)
                if check_password(password, student.password):
                    # Store student session
                    request.session["student_id"] = student.id
                    request.session["student_name"] = student.full_name
                    messages.success(request, f"Welcome {student.full_name}!")
                    return redirect("student_dashboard")
                else:
                    messages.error(request, "Incorrect password.")
            except Student.DoesNotExist:
                messages.error(request, "Invalid Student ID.")

    return render(request, "student/register_login.html")


# ----- Student Dashboard -----
# student/views.py
from django.shortcuts import render, redirect, get_object_or_404
from student.models import Student
from adminui.models import Problem
from .models import Submission

def student_dashboard(request):
    # Get logged-in student from session
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("register_login")

    student = get_object_or_404(Student, id=student_id)

    # All submissions of this student
    submissions = Submission.objects.filter(student=student).order_by("-submitted_at")

    # Problems student already submitted
    submitted_problem_ids = submissions.values_list("problem_id", flat=True)

    # Next available problem
    next_problem = Problem.objects.exclude(id__in=submitted_problem_ids).order_by("created_at").first()

    return render(request, "student/student_dashboard.html", {
        "student": student,
        "next_problem": next_problem,   # next unsolved problem
        "submissions": submissions,     # list of all submissions
    })





# ----- Submit Solution -----
def submit_solution(request, problem_id):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("register_login")

    student = get_object_or_404(Student, id=student_id)
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            Submission.objects.create(
                problem=problem,
                student=student,
                file=file
            )
        return redirect("student_dashboard")



# ----- Logout -----
def student_logout(request):
    request.session.flush()  # clear all session data
    messages.success(request, "Logged out successfully!")
    return redirect("register_login")
