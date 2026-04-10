from django.contrib import admin
from .models import Lesson, FeedbackRecord

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