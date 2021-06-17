from django.db.models import Count, Q, Prefetch
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Quiz, Question, Answer, UserAnswerOptions, QuestionAnswerOptions
from .serializers import QuizSerializer, QuestionSerializer, QuizUserAnswerSerializer, AnswerSerializer


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()

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

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return []


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.prefetch_related().all()
    http_method_names = ['get', 'post', ]


class QuizUserAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = QuizUserAnswerSerializer
    queryset = Quiz.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        queryset = super().get_queryset()

        user_id = self.request.query_params.get('user')
        if user_id:
            prefetch_answers = Answer.objects.filter(user_id=user_id)

            prefetch_questions = Question.objects.annotate(
                answer_count=Count('answer', filter=Q(answer__user_id=user_id))
            ).filter(
                answer_count__gt=0
            ).prefetch_related(
                Prefetch('answer', queryset=prefetch_answers)
            )

            queryset = Quiz.objects.annotate(
                questions_count=Count('questions', filter=Q(questions__answer__user_id=user_id))
            ).filter(
                questions_count__gt=0
            ).prefetch_related(
                Prefetch('questions', queryset=prefetch_questions)
            ).order_by('id')

        return queryset
