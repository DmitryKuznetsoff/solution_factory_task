from django.db.models import Count, Q, Prefetch
from django_filters import rest_framework as filters
from api.models import Quiz, Question, Answer


class QuizFilter(filters.FilterSet):
    class Meta:
        model = Quiz
        fields = '__all__'


class QuestionFilter(filters.FilterSet):
    class Meta:
        model = Question
        fields = '__all__'


class AnswerFilter(filters.FilterSet):
    class Meta:
        model = Answer
        fields = '__all__'


class QuizUserAnswerFilter(filters.FilterSet):
    user = filters.CharFilter(method='filter_by_user')

    def filter_by_user(self, queryset, name, value):
        prefetch_answers = Answer.objects.filter(user_id=value)

        prefetch_questions = Question.objects.annotate(
            answer_count=Count('answer', filter=Q(answer__user_id=value))
        ).filter(
            answer_count__gt=0
        ).prefetch_related(
            Prefetch('answer', queryset=prefetch_answers)
        )

        queryset = Quiz.objects.annotate(
            questions_count=Count('questions', filter=Q(questions__answer__user_id=value))
        ).filter(
            questions_count__gt=0
        ).prefetch_related(
            Prefetch('questions', queryset=prefetch_questions)
        ).order_by('id')

        return queryset


class Meta:
    model = Quiz
    fields = '__all__'
