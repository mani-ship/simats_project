from django.shortcuts import render, redirect
from django.contrib import messages
from adminui.models import Faculty
from student.models import Problem, Submission  # import student models

def faculty_login(request):
    # If already logged in → go to dashboard
    if request.session.get('faculty_id'):
        return redirect('faculty_dashboard')

    if request.method == 'POST':
        faculty_id_input = request.POST.get('faculty_id')
        password_input = request.POST.get('password')

        if not faculty_id_input or not password_input:
            messages.error(request, "Please enter Faculty ID and Password.")
            return render(request, "faculty/login.html")

        faculty_id_input = faculty_id_input.strip()
        password_input = password_input.strip()

        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id_input)
            if faculty.password == password_input:  # plain text check
                request.session['faculty_id'] = faculty.faculty_id
                request.session['faculty_username'] = faculty.username
                return redirect('faculty_dashboard')
            else:
                messages.error(request, "Incorrect password.")
        except Faculty.DoesNotExist:
            messages.error(request, "Faculty ID does not exist.")

    return render(request, "faculty/login.html")




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from student.models import Submission

from .decorators import faculty_login_required

@faculty_login_required
def faculty_dashboard(request):
    # Fetch all submissions with student info
    submissions = Submission.objects.select_related('student', 'problem').all().order_by('-submitted_at')
    
    return render(request, "faculty/dashboard.html", {
        "faculty_username": request.user.username,
        "submissions": submissions
    })






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from student.models import Submission

def evaluate_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if request.method == "POST":
        marks = request.POST.get("marks")
        remarks = request.POST.get("remarks")

        try:
            marks = int(marks)
            if marks > submission.problem.total_marks:
                messages.error(request, f"Marks cannot exceed {submission.problem.total_marks}")
            else:
                submission.faculty_marks = marks
                submission.faculty_remarks = remarks
                submission.save()  # ✅ Saves in database
                messages.success(request, "Evaluation saved successfully!")
                return redirect("faculty_dashboard")
        except ValueError:
            messages.error(request, "Please enter valid marks.")

    return render(request, "faculty/evaluate_submission.html", {"submission": submission})





def faculty_logout(request):
    request.session.flush()  # clear session
    return redirect('faculty_login')
