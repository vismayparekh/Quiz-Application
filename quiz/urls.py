"""
URL configuration for quizproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

app_name = "quiz"

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('teacher/', views.TeacherRegister, name='TeacherRegister'),
    path('student/', views.StudentRegister, name='StudentRegister'),
    path('teacherlogin/', views.TeacherLoginView, name='LoginTeacher'),
    path('studentlogin/', views.StudentLoginView, name='LoginStudent'),
    path('teacher_dashboard/<int:TeacherID>/', views.teacher_dashboard, name='teacher_dashboard'),  
    path('student_dashboard/<int:StuID>/', views.student_dashboard, name='student_dashboard'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),  
    path('edit_quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('delete_quiz/<int:quiz_id>/<int:teacher_id>/', views.delete_quiz, name='delete_quiz'),
    path('take_quiz/<int:stu_id>/<str:quiz_name>/', views.take_quiz, name='take_quiz'),
    path('show_results/<int:stu_id>/', views.show_results, name='show_results'),
    path('view_quiz/<int:quiz_id>/', views.view_quiz, name='view_quiz'),
]

