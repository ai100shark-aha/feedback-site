from django.contrib import admin
from django.urls import path
from feedback import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # ── keep-alive ──
    path('ping/', views.ping, name='ping'),
    # ── 기존 피드백 시스템 ──
    path('', views.index, name='index'),
    path('write/<int:lesson_id>/', views.feedback_create, name='feedback_create'),
    path('result/<int:lesson_id>/', views.lesson_result, name='lesson_result'),
    path('edit/<int:lesson_id>/<str:student_id>/', views.feedback_edit, name='feedback_edit'),
    path('student/<str:student_id>/', views.student_summary, name='student_summary'),
    # ── 활동문제 채점 시스템 ──
    path('guide/upload/', views.guide_upload, name='guide_upload'),       # 지도서 1회 업로드
    path('quiz/generate/', views.quiz_generate, name='quiz_generate'),    # 범위 설정 → 문제 생성
    path('quiz/<int:lesson_id>/', views.quiz_solve, name='quiz_solve'),
    path('quiz/<int:lesson_id>/submit/', views.quiz_submit, name='quiz_submit'),
    path('quiz/<int:lesson_id>/result/', views.quiz_result, name='quiz_result'),
    # ── 교사 관리 ──
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quiz/<int:quizset_id>/', views.teacher_quiz_detail, name='teacher_quiz_detail'),
    path('teacher/grade/<int:quizset_id>/<int:lesson_id>/<str:student_id>/',
         views.teacher_grade_student, name='teacher_grade_student'),
    # ── 피드백 리포트 ──
    path('teacher/report/', views.teacher_report, name='teacher_report'),
    path('teacher/report/excel/', views.teacher_report_excel, name='teacher_report_excel'),
    # ── 학번 검증/정정 ──
    path('teacher/validate/', views.teacher_validate_ids, name='teacher_validate_ids'),
    path('teacher/validate/excel/', views.teacher_validate_excel, name='teacher_validate_excel'),
    # ── 중복 제거 ──
    path('teacher/dedup/', views.teacher_dedup, name='teacher_dedup'),
]
