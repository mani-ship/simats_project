# adminui/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from student.models import Student, Submission
from adminui.models import Problem, Faculty
from datetime import datetime


# ----- Admin Access Decorator -----
def admin_required(view_func):
    """Decorator to allow only logged-in staff users."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first!")
            return redirect("login_options")
        if not request.user.is_staff:
            messages.error(request, "You are not authorized to access this page!")
            return redirect("login_options")
        return view_func(request, *args, **kwargs)
    return wrapper


# ----- Login Views -----
def login_options(request):
    return render(request, "adminui/login_options.html")


from django.contrib import messages

def login_view(request):
    # Clear previous messages so login page is clean
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # This iterates and clears old messages

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:   # only staff/superuser
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials or not an admin user")

    return render(request, "adminui/login.html")



@admin_required
def logout_view(request):
    logout(request)
    
    return redirect("login_options")


# ----- Dashboard -----
@admin_required
def dashboard(request):
    student_count = Student.objects.count()
    faculty_count = Faculty.objects.count()
    problem_count = Problem.objects.count()

    # Get all submissions with related student, faculty, problem (sorted latest first)
    submissions = Submission.objects.select_related("student", "faculty", "problem").order_by("-submitted_at")

    # Pagination
    paginator = Paginator(submissions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "student_count": student_count,
        "faculty_count": faculty_count,
        "problem_count": problem_count,
        "page_obj": page_obj,
    }
    return render(request, "adminui/dashboard.html", context)


# ----- Student List -----
@admin_required
def student_list(request):
    query = request.GET.get("q", "")

    if query:
        students = Student.objects.filter(full_name__icontains=query) | Student.objects.filter(student_id__icontains=query)
    else:
        students = Student.objects.all()

    paginator = Paginator(students, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "adminui/student_list.html", {
        "page_obj": page_obj,
        "query": query
    })


# ----- Change Student Password -----
@admin_required
def student_change_password(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
        else:
            student.set_password(new_password)
            student.save()
            messages.success(request, f"Password updated for {student.full_name}")

    return redirect("student_list")


# ----- Faculty CRUD -----
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from .models import Faculty
from .decorators import admin_required


@admin_required
def faculty_list(request):
    """List all faculties with optional search and pagination."""
    search_query = request.GET.get("search", "")
    faculties = Faculty.objects.all()

    if search_query:
        faculties = faculties.filter(faculty_id__icontains=search_query)

    paginator = Paginator(faculties, 7)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search_query,
    }
    return render(request, "adminui/faculty_list.html", context)


@admin_required
def add_faculty(request):
    """Add a new faculty member with username, password, and other info."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        faculty_id = request.POST.get("faculty_id")
        gender = request.POST.get("gender")
        department = request.POST.get("department")

        # Validate required fields
        if not all([username, password, faculty_id, gender, department]):
            messages.error(request, "All fields are required.")
            return redirect("faculty_list")

        # Check uniqueness
        if Faculty.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("faculty_list")

        if Faculty.objects.filter(faculty_id=faculty_id).exists():
            messages.error(request, "Faculty ID already exists.")
            return redirect("faculty_list")

        # Create new faculty with hashed password
        Faculty.objects.create(
            username=username,
            password=make_password(password),
            faculty_id=faculty_id,
            gender=gender,
            department=department
        )

        messages.success(request, "Faculty added successfully.")
        return redirect("faculty_list")

    return redirect("faculty_list")


@admin_required
def edit_faculty(request, pk):
    """Edit an existing faculty member's details; password is optional."""
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")  # optional
        faculty_id = request.POST.get("faculty_id")
        gender = request.POST.get("gender")
        department = request.POST.get("department")

        # Check uniqueness
        if Faculty.objects.filter(username=username).exclude(pk=pk).exists():
            messages.error(request, "Username already exists.")
            return redirect("faculty_list")

        if Faculty.objects.filter(faculty_id=faculty_id).exclude(pk=pk).exists():
            messages.error(request, "Faculty ID already exists.")
            return redirect("faculty_list")

        # Update fields
        faculty.username = username
        faculty.faculty_id = faculty_id
        faculty.gender = gender
        faculty.department = department

        if password:
            faculty.password = make_password(password)  # update password only if provided

        faculty.save()
        messages.success(request, "Faculty updated successfully.")
        return redirect("faculty_list")

    return redirect("faculty_list")




@admin_required
def delete_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    faculty.delete()
    messages.success(request, "Faculty deleted successfully.")
    return redirect("faculty_list")


# ----- Problem CRUD -----
@admin_required
def problem_upload(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        total_marks = request.POST.get("total_marks")

        if not title or not description or not total_marks:
            messages.error(request, "All fields are required!")
            return redirect('problem_upload')

        Problem.objects.create(
            title=title,
            description=description,
            total_marks=total_marks
        )
        messages.success(request, "Problem uploaded successfully!")
        return redirect('problem_upload')

    problems = Problem.objects.all().order_by('-created_at')
    selected_date = request.GET.get('date', '')

    if selected_date:
        problems = problems.filter(created_at__date=selected_date)

    paginator = Paginator(problems, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'problems': page_obj,
        'today': datetime.today().strftime('%d.%m.%Y'),
        'now_time': datetime.now().strftime('%I:%M %p'),
        'selected_date': selected_date
    }
    return render(request, "adminui/problem_upload.html", context)


from .decorators import admin_required

@admin_required
def delete_problem(request, pk):
    from .models import Problem
    from django.shortcuts import get_object_or_404, redirect

    problem = get_object_or_404(Problem, pk=pk)
    problem.delete()
    return redirect('problem_upload')