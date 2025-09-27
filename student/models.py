# student/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Student(models.Model):
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # store hashed password
    gender = models.CharField(max_length=10)
    year = models.IntegerField()
    semester = models.IntegerField()
    department = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.student_id
from adminui.models import Problem,Faculty


class Submission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to="submissions/")
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Link evaluation to Faculty, not admin User
    faculty = models.ForeignKey(
    Faculty,
    on_delete=models.SET_NULL,
    null=True,      # important
    blank=True,
    related_name="evaluated_submissions"
)
    faculty_marks = models.IntegerField(null=True, blank=True)
    faculty_remarks = models.TextField(blank=True)

    def __str__(self):
        faculty_display = self.faculty.username if self.faculty else "Not Evaluated"
        return f"{self.student.full_name} - {self.problem.title} (Evaluated by: {faculty_display})"
