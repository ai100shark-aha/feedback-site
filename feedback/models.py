from django.db import models


# ─────────────────────────────────────────────
# 기존 모델 (수업 피드백)
# ─────────────────────────────────────────────
class Lesson(models.Model):
    """수업 회차 관리"""
    title      = models.CharField(max_length=100)  # 예: 12차시 - 표준입출력
    date       = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} | {self.title}"

class FeedbackRecord(models.Model):
    """학생 수업 피드백 기록"""
    lesson       = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='records')

    # 학생 정보
    student_id   = models.CharField(max_length=10)   # 학번
    student_num  = models.CharField(max_length=5)    # 번호
    student_name = models.CharField(max_length=20)   # 이름

    # 5가지 피드백 항목
    summary      = models.TextField()   # 핵심 개념 3가지
    problem      = models.TextField()   # 오류/어려움과 해결
    career       = models.TextField()   # 진로 연결
    deeplearn    = models.TextField()   # 심화 학습 의지
    peer         = models.TextField()   # 칭찬 한마디

    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson} | {self.student_num}번 {self.student_name}"

    class Meta:
        ordering = ['student_num']


# ─────────────────────────────────────────────
# 활동문제 채점 시스템
# ─────────────────────────────────────────────

class QuizSet(models.Model):
    """교사가 등록한 차시별 문제 세트"""
    chapter_num = models.IntegerField(unique=True)        # 차시 번호 (1~39)
    title       = models.CharField(max_length=100)        # 예: "3차시 – 조건문 활동문제"
    guide_text  = models.TextField()                      # 지도서 PDF 추출 텍스트
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.chapter_num}차시 – {self.title}"


class Question(models.Model):
    """QuizSet 내 개별 문제"""
    quizset      = models.ForeignKey(QuizSet, on_delete=models.CASCADE, related_name='questions')
    number       = models.IntegerField()       # 문제 번호
    content      = models.TextField()          # 문제 내용
    model_answer = models.TextField()          # 모범 답안
    score        = models.IntegerField(default=10)  # 배점

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Q{self.number}: {self.content[:40]}"


class StudentAnswer(models.Model):
    """학생이 제출한 답안 + AI/교사 채점 결과"""
    question     = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    lesson_id    = models.IntegerField()          # 어느 반·차시인지 (LESSONS id)
    student_id   = models.CharField(max_length=10)
    student_num  = models.CharField(max_length=5)
    student_name = models.CharField(max_length=20)

    # 답안 (세 가지 중 하나 이상)
    answer_text  = models.TextField(blank=True)   # 텍스트 답안
    answer_code  = models.TextField(blank=True)   # 코드 답안
    answer_image = models.TextField(blank=True)   # base64 JPEG (리사이즈 후)

    # 채점
    score            = models.IntegerField(null=True, blank=True)
    max_score        = models.IntegerField(default=10)
    ai_feedback      = models.TextField(blank=True)
    teacher_feedback = models.TextField(blank=True)
    is_confirmed     = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering      = ['student_num', 'question__number']
        unique_together = [['question', 'student_id']]

    def __str__(self):
        return f"{self.student_name}({self.student_id}) – Q{self.question.number}"