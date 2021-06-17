from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

QUESTION_TYPE_CHOICES = (
    ('TEXT', 'TEXT'),
    ('SINGLE_ANSWER_OPTION', 'SINGLE_ANSWER_OPTION'),
    ('MULTIPLE_ANSWER_OPTION', 'MULTIPLE_ANSWER_OPTION'),
)


class Quiz(models.Model):
    """
    Модель для опросов
    """
    title = models.TextField(null=False, blank=False)
    start_date = models.DateField(null=False, blank=False, default=timezone.localdate())
    end_date = models.DateField(null=False, blank=False, default=timezone.localdate())
    description = models.TextField()


class Question(models.Model):
    """
    Модель для вопросов
    """
    text = models.TextField(null=False, blank=False)
    type = models.CharField(choices=QUESTION_TYPE_CHOICES, max_length=30, default='TEXT')
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)


class QuestionAnswerOptions(models.Model):
    """
    Модель для вариантов ответов на вопросы
    """
    name = models.TextField(null=False, blank=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')


class Answer(models.Model):
    """
    Модель для ответов
    """
    text = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='user', null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answer', on_delete=models.CASCADE)


class UserAnswerOptions(models.Model):
    answer_option = models.ForeignKey(QuestionAnswerOptions, on_delete=models.CASCADE, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='user_answer_options', null=True)
