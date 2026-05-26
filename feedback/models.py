from django.db import models


# ─────────────────────────────────────────────
# 기존 모델 (수업 피드백)
# ─────────────────────────────────────────────
class Lesson(models.Model):
    """수업 회차 관리"""
    title      = models.CharField(max_length=100)
    date       = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} | {self.title}"

class FeedbackRecord(models.Model):
    """학생 수업 피드백 기록"""
    lesson       = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='records')
    student_id   = models.CharField(max_length=10)
    student_num  = models.CharField(max_length=5)
    student_name = models.CharField(max_length=20)
    summary      = models.TextField()
    problem      = models.TextField()
    career       = models.TextField()
    deeplearn    = models.TextField()
    peer         = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson} | {self.student_num}번 {self.student_name}"

    class Meta:
        ordering = ['student_num']


# ─────────────────────────────────────────────
# 활동문제 채점 시스템
# ─────────────────────────────────────────────

class GuideBook(models.Model):
    """교사가 1회 업로드하는 교사용 지도서 (전체 텍스트 보관)"""
    name        = models.CharField(max_length=200)   # 예: "정보 교과서 지도서 2026"
    full_text   = models.TextField()                 # PDF 전체 텍스트
    page_count  = models.IntegerField(default=0)     # 총 페이지 수
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.page_count}p)"

    class Meta:
        ordering = ['-uploaded_at']


class QuizSet(models.Model):
    """차시별 문제 세트 (지도서의 특정 범위에서 생성)"""
    guidebook   = models.ForeignKey(GuideBook, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='quizsets')
    chapter_num = models.IntegerField(unique=True)   # 차시 번호 (1~39)
    title       = models.CharField(max_length=200)   # 예: "3차시 – 조건문"
    # 범위 정보 (문제 생성 시 사용)
    range_topic = models.CharField(max_length=200, blank=True)  # 주제/단원명
    range_pages = models.CharField(max_length=50, blank=True)   # 페이지 범위 (예: 45-62)
    range_text  = models.TextField(blank=True)                  # 해당 범위 추출 텍스트 (캐시)
    # 상태
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.chapter_num}차시 – {self.title}"


class Question(models.Model):
    """QuizSet 내 개별 문제"""
    quizset      = models.ForeignKey(QuizSet, on_delete=models.CASCADE, related_name='questions')
    number       = models.IntegerField()
    content      = models.TextField()
    model_answer = models.TextField()
    score        = models.IntegerField(default=10)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Q{self.number}: {self.content[:40]}"


class StudentAnswer(models.Model):
    """학생이 제출한 답안 + AI/교사 채점 결과"""
    question     = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    lesson_id    = models.IntegerField()
    student_id   = models.CharField(max_length=10)
    student_num  = models.CharField(max_length=5)
    student_name = models.CharField(max_length=20)
    answer_text  = models.TextField(blank=True)
    answer_code  = models.TextField(blank=True)
    answer_image = models.TextField(blank=True)
    score            = models.IntegerField(null=True, blank=True)
    max_score        = models.IntegerField(default=10)
    ai_feedback      = models.TextField(blank=True)
    teacher_feedback = models.TextField(blank=True)
    is_confirmed     = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering        = ['student_num', 'question__number']
        unique_together = [['question', 'student_id']]

    def __str__(self):
        return f"{self.student_name}({self.student_id}) – Q{self.question.number}"
