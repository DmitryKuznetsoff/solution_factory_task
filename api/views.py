from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .filters import QuizFilter, QuestionFilter, AnswerFilter, QuizUserAnswerFilter
from .models import Quiz, Question, Answer
from .serializers import QuizSerializer, QuestionSerializer, QuizUserAnswerSerializer, AnswerSerializer


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    filterset_class = QuizFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        # Если пользователь не является администратором, выдаём только опросы с актуальной датой:
        if not self.request.user.is_staff:
            queryset = queryset.filter(end_date__gt=timezone.localdate()).all()
        return queryset


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    filterset_class = QuestionFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return []


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.prefetch_related().all()
    http_method_names = ['get', 'post', ]
    filterset_class = AnswerFilter


class QuizUserAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = QuizUserAnswerSerializer
    queryset = Quiz.objects.all()
    http_method_names = ['get', ]
    filterset_class = QuizUserAnswerFilter
