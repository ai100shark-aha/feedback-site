from django.shortcuts import render, redirect, get_object_or_404
from .models import Lesson, FeedbackRecord
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

def get_sheet():
    import json
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key('1A7awsXWOu-WPiRjY6vk8rPEhBh8PpGiTp3pGAlellsM').sheet1
    return sheet

def index(request):
    lessons = Lesson.objects.all().order_by('-date')
    return render(request, 'feedback/index.html', {'lessons': lessons})

def feedback_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        student_id   = request.POST['student_id']
        student_num  = request.POST['student_num']
        student_name = request.POST['student_name']
        summary      = request.POST['summary']
        problem      = request.POST['problem']
        career       = request.POST['career']
        deeplearn    = request.POST['deeplearn']
        peer         = request.POST['peer']

        # 중복 제출 확인 (같은 수업 + 같은 학번)
        already = FeedbackRecord.objects.filter(
            lesson=lesson,
            student_id=student_id
        ).exists()

        if not already:
            # Django DB 저장
            FeedbackRecord.objects.create(
                lesson       = lesson,
                student_id   = student_id,
                student_num  = student_num,
                student_name = student_name,
                summary      = summary,
                problem      = problem,
                career       = career,
                deeplearn    = deeplearn,
                peer         = peer,
            )

            # 구글 시트 백그라운드 저장
            import threading
            def save_to_sheet():
                try:
                    sheet = get_sheet()
                    sheet.append_row([
                        datetime.now().strftime('%Y-%m-%d %H:%M'),
                        str(lesson),
                        student_id,
                        student_num,
                        student_name,
                        summary,
                        problem,
                        career,
                        deeplearn,
                        peer,
                    ])
                except Exception as e:
                    print(f"구글 시트 저장 오류: {e}")

            threading.Thread(target=save_to_sheet).start()

        return render(request, 'feedback/done.html', {
            'lesson': lesson,
            'already': already,
        })

    return render(request, 'feedback/create.html', {'lesson': lesson})

def lesson_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
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