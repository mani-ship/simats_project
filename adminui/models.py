from django.db import models

class Faculty(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)   # (later we can use hashing)
    faculty_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=[
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other")
    ])
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.username} ({self.department})"


from django.db import models

class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    total_marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)  # stores upload date automatically

    def __str__(self):
        return self.title

