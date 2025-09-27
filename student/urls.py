from django.urls import path
from . import views

urlpatterns = [
    path("auth/", views.register_login, name="student_auth"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/submit/<int:problem_id>/", views.submit_solution, name="submit_solution"),
    path("student/logout/", views.student_logout, name="student_logout"),  # add logout
]
