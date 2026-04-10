from django.shortcuts import render, redirect, get_object_or_404
from .models import Lesson, FeedbackRecord

def index(request):
    lessons = Lesson.objects.all().order_by('-date')
    return render(request, 'feedback/index.html', {'lessons': lessons})

def feedback_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        FeedbackRecord.objects.create(
            lesson       = lesson,
            student_id   = request.POST['student_id'],
            student_num  = request.POST['student_num'],
            student_name = request.POST['student_name'],
            summary      = request.POST['summary'],
            problem      = request.POST['problem'],
            career       = request.POST['career'],
            deeplearn    = request.POST['deeplearn'],
            peer         = request.POST['peer'],
        )
        return render(request, 'feedback/done.html', {'lesson': lesson})
    return render(request, 'feedback/create.html', {'lesson': lesson})

def lesson_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # 학번 입력 전: 검색 화면만 표시
    student_id = request.GET.get('student_id', '').strip()
    record     = None
    error      = None

    if student_id:
        try:
            record = FeedbackRecord.objects.get(lesson=lesson, student_id=student_id)
        except FeedbackRecord.DoesNotExist:
            error = "해당 학번의 제출 기록이 없습니다."

    return render(request, 'feedback/result.html', {
        'lesson': lesson,
        'record': record,
        'error': error,
        'student_id': student_id,
    })

def student_summary(request, student_id):
    records = FeedbackRecord.objects.filter(
        student_id=student_id
    ).order_by('lesson__date')
    if not records.exists():
        return render(request, 'feedback/not_found.html')
    student_name = records.first().student_name
    return render(request, 'feedback/student_summary.html', {
        'records': records,
        'student_name': student_name,
        'student_id': student_id,
        'count': records.count(),
    })