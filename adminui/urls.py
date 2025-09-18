from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_options, name="login_options"),  # the landing page
    path("admin_login", views.login_view, name="login"),          # login page
    path("dashboard/", views.dashboard, name="dashboard"),  # custom admin dashboard
    path("logout/", views.logout_view, name="logout"), # logout
     path("faculty/", views.faculty_list, name="faculty_list"),
    path("faculty/add/", views.add_faculty, name="add_faculty"),
    path("faculty/edit/<int:pk>/", views.edit_faculty, name="edit_faculty"),
    path("faculty/delete/<int:pk>/", views.delete_faculty, name="delete_faculty"),
    path('problem/upload/', views.problem_upload, name='problem_upload'),
    path("students/", views.student_list, name="student_list"),
    path("students/<int:student_id>/change-password/", views.student_change_password, name="student_change_password"),
    path('problem/delete/<int:pk>/', views.delete_problem, name='delete_problem'),
]
