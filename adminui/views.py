from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# adminui/views.py
from django.shortcuts import render

def login_options(request):
    return render(request, "adminui/login_options.html")


def login_view(request):
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

@login_required

def dashboard(request):
    return render(request, "adminui/dashboard.html")

def logout_view(request):
    logout(request)
    return redirect("login")





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Faculty

# List & Search Faculties
def faculty_list(request):
    search = request.GET.get("search", "")
    if search:
        faculties = Faculty.objects.filter(faculty_id__icontains=search)
    else:
        faculties = Faculty.objects.all()
    return render(request, "adminui/faculty_list.html", {"faculties": faculties})


# Add Faculty
def add_faculty(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        faculty_id = request.POST.get("facultyId")
        gender = request.POST.get("gender")
        department = request.POST.get("department")

        # Validation
        if not username or not password or not faculty_id or not department or not gender:
            messages.error(request, "All fields are required.")
            return redirect("faculty_list")

        if Faculty.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("faculty_list")

        if Faculty.objects.filter(faculty_id=faculty_id).exists():
            messages.error(request, "Faculty ID already exists.")
            return redirect("faculty_list")

        # Save to database
        Faculty.objects.create(
            username=username,
            password=password,  # optionally hash the password
            faculty_id=faculty_id,
            gender=gender,
            department=department
        )
        messages.success(request, "Faculty added successfully.")
        return redirect("faculty_list")

    return redirect("faculty_list")


# Edit Faculty
def edit_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        faculty_id = request.POST.get("facultyId")
        gender = request.POST.get("gender")
        department = request.POST.get("department")

        # Validation
        if Faculty.objects.filter(username=username).exclude(pk=pk).exists():
            messages.error(request, "Username already exists.")
            return redirect("faculty_list")

        if Faculty.objects.filter(faculty_id=faculty_id).exclude(pk=pk).exists():
            messages.error(request, "Faculty ID already exists.")
            return redirect("faculty_list")

        # Update database
        faculty.username = username
        faculty.password = password  # optionally hash the password
        faculty.faculty_id = faculty_id
        faculty.gender = gender
        faculty.department = department
        faculty.save()

        messages.success(request, "Faculty updated successfully.")
        return redirect("faculty_list")

    return redirect("faculty_list")


# Delete Faculty
def delete_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    faculty.delete()
    messages.success(request, "Faculty deleted successfully.")
    return redirect("faculty_list")


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Problem
from datetime import datetime

def problem_upload(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        total_marks = request.POST.get("total_marks")   # ✅ FIX

        if not title or not description or not total_marks:
            messages.error(request, "All fields are required!")
            return redirect('problem_upload')

        Problem.objects.create(
            title=title,
            description=description,
            total_marks=total_marks   # ✅ FIX
        )
        messages.success(request, "Problem uploaded successfully!")
        return redirect('problem_upload')

    problems = Problem.objects.all().order_by('-created_at')
    selected_date = request.GET.get('date', '')

    if selected_date:
        problems = problems.filter(created_at__date=selected_date)

    context = {
        'problems': problems,
        'today': datetime.today().strftime('%d.%m.%Y'),
        'now_time': datetime.now().strftime('%I:%M %p'),
        'selected_date': selected_date
    }
    return render(request, "adminui/problem_upload.html", context)



def delete_problem(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    problem.delete()
    messages.success(request, "Problem deleted successfully!")
    return redirect('problem_upload')


# adminui/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from student.models import Student

# ✅ Show all registered students
def student_list(request):
    query = request.GET.get("q", "")
    if query:
        students = Student.objects.filter(full_name__icontains=query) | Student.objects.filter(student_id__icontains=query)
    else:
        students = Student.objects.all()

    return render(request, "adminui/student_list.html", {"students": students, "query": query})


# ✅ Change password page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from student.models import Student

def student_change_password(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
        else:
            # ✅ Use set_password() so password gets hashed
            student.set_password(new_password)
            student.save()
            messages.success(request, f"Password updated for {student.full_name}")
            return redirect("student_list")  # back to student list page

    return render(request, "adminui/student_change_password.html", {"student": student})

