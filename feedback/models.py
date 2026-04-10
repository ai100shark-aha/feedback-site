from django.db import models

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