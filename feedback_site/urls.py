from django.contrib import admin
from django.urls import path
from feedback import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # ── 기존 피드백 시스템 ──
    path('', views.index, name='index'),
    path('write/<int:lesson_id>/', views.feedback_create, name='feedback_create'),
    path('result/<int:lesson_id>/', views.lesson_result, name='lesson_result'),
    path('edit/<int:lesson_id>/<str:student_id>/', views.feedback_edit, name='feedback_edit'),
    path('student/<str:student_id>/', views.student_summary, name='student_summary'),
    # ── 활동문제 채점 시스템 ──
    path('quiz/upload/', views.quiz_upload, name='quiz_upload'),
    path('quiz/<int:lesson_id>/', views.quiz_solve, name='quiz_solve'),
    path('quiz/<int:lesson_id>/submit/', views.quiz_submit, name='quiz_submit'),
    path('quiz/<int:lesson_id>/result/', views.quiz_result, name='quiz_result'),
    # ── 교사 관리 ──
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quiz/<int:quizset_id>/', views.teacher_quiz_detail, name='teacher_quiz_detail'),
    path('teacher/grade/<int:quizset_id>/<int:lesson_id>/<str:student_id>/',
         views.teacher_grade_student, name='teacher_grade_student'),
]
