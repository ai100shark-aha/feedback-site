from django.contrib import admin
from .models import Lesson, FeedbackRecord, QuizSet, Question, StudentAnswer

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['date', 'title', 'record_count']

    def record_count(self, obj):
        return obj.records.count()
    record_count.short_description = '제출 수'

@admin.register(FeedbackRecord)
class FeedbackRecordAdmin(admin.ModelAdmin):
    list_display  = ['lesson', 'student_num', 'student_name', 'student_id', 'created_at']
    list_filter   = ['lesson']
    search_fields = ['student_name', 'student_id']


@admin.register(QuizSet)
class QuizSetAdmin(admin.ModelAdmin):
    list_display = ['chapter_num', 'title', 'question_count', 'is_active', 'updated_at']
    list_filter  = ['is_active']

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = '문제 수'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ['quizset', 'number', 'content_short', 'score']
    list_filter   = ['quizset']

    def content_short(self, obj):
        return obj.content[:40]
    content_short.short_description = '문제'


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display  = ['student_name', 'student_id', 'question', 'score', 'max_score', 'is_confirmed', 'created_at']
    list_filter   = ['is_confirmed', 'question__quizset']
    search_fields = ['student_name', 'student_id']