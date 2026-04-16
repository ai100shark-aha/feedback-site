from django.contrib import admin
from django.urls import path
from feedback import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('write/<int:lesson_id>/', views.feedback_create, name='feedback_create'),
    path('result/<int:lesson_id>/', views.lesson_result, name='lesson_result'),
    path('edit/<int:lesson_id>/<str:student_id>/', views.feedback_edit, name='feedback_edit'),
    path('student/<str:student_id>/', views.student_summary, name='student_summary'),
]