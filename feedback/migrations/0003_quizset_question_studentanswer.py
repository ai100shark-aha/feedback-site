from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_feedbackrecord_lesson_delete_feedback_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chapter_num', models.IntegerField(unique=True)),
                ('title', models.CharField(max_length=100)),
                ('guide_text', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('content', models.TextField()),
                ('model_answer', models.TextField()),
                ('score', models.IntegerField(default=10)),
                ('quizset', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='questions',
                    to='feedback.quizset',
                )),
            ],
            options={
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_id', models.IntegerField()),
                ('student_id', models.CharField(max_length=10)),
                ('student_num', models.CharField(max_length=5)),
                ('student_name', models.CharField(max_length=20)),
                ('answer_text', models.TextField(blank=True)),
                ('answer_code', models.TextField(blank=True)),
                ('answer_image', models.TextField(blank=True)),
                ('score', models.IntegerField(blank=True, null=True)),
                ('max_score', models.IntegerField(default=10)),
                ('ai_feedback', models.TextField(blank=True)),
                ('teacher_feedback', models.TextField(blank=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='student_answers',
                    to='feedback.question',
                )),
            ],
            options={
                'ordering': ['student_num', 'question__number'],
                'unique_together': {('question', 'student_id')},
            },
        ),
    ]
