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


from django.db import models
from django.contrib.auth.models import User
from adminui.models import Problem
from student.models import Student


class Submission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to="submissions/")
    submitted_at = models.DateTimeField(auto_now_add=True)

    faculty = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluated_submissions"
    )
    faculty_name = models.CharField(max_length=255, null=True, blank=True)  # store snapshot
    faculty_marks = models.IntegerField(null=True, blank=True)
    faculty_remarks = models.TextField()


    def save(self, *args, **kwargs):
        # store faculty name when faculty is assigned
        if self.faculty:
            self.faculty_name = self.faculty.get_full_name() or self.faculty.username
        super().save(*args, **kwargs)

    def __str__(self):
        faculty_display = self.faculty_name if self.faculty_name else "Not Evaluated"
        return f"{self.student.full_name} - {self.problem.title} (Evaluated by: {faculty_display})"


