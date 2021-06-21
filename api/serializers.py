from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Quiz, Question, Answer, QuestionAnswerOptions, UserAnswerOptions


class UserAnswerOptionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выбранных пользователем вариантов ответов
    """

    class Meta:
        model = UserAnswerOptions
        fields = ['answer_option', ]


class QuestionsAnswerOptionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вариантов ответа на вопрос
    """

    class Meta:
        model = QuestionAnswerOptions
        fields = ['id', 'name', ]


class AnswerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ответов
    """

    user_answer_options = UserAnswerOptionsSerializer(many=True)

    class Meta:
        model = Answer
        fields = ['id', 'text', 'question', 'user', 'user_answer_options', ]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        question_id = request.data.get('question')
        try:
            question_obj = Question.objects.get(id=question_id)
            if question_obj.type == 'TEXT':
                fields['text'].required = True
                fields['user_answer_options'].required = False
        except Question.DoesNotExist:
            pass

        return fields

    def validate(self, attrs):
        user = self.context['request'].user
        question = attrs['question']
        user_answer_options = attrs.get('user_answer_options')

        # Валидация пользователя:
        if isinstance(user, AnonymousUser):
            attrs.update({'user': None})
        else:
            check_answer = Answer.objects.filter(user=user, question=question)
            if check_answer:
                raise ValidationError({'ValidationError': 'Вы уже ответили на данный вопрос'})
            attrs.update({'user': user})

        # Валидация ответов по типу вопроса:
        if question.type == 'TEXT':
            try:
                attrs.pop('user_answer_options')
            except KeyError:
                pass
        elif question.type == 'SINGLE_ANSWER_OPTION':
            if len(user_answer_options) != 1:
                raise ValidationError({
                    'ValidationError': 'Для вопроса с типом "SINGLE_ANSWER_OPTION" '
                                       'должно быть заполнен один вариант ответа'})
        elif question.type == 'MULTIPLE_ANSWER_OPTION':
            if len(user_answer_options) < 1:
                raise ValidationError({
                    'ValidationError': 'Для вопроса с типом "MULTIPLE_ANSWER_OPTION" '
                                       'должно быть заполнен хотя бы один вариант ответа'})

        if user_answer_options:
            try:
                attrs.pop('text')
            except KeyError:
                pass

            existing_answer_options_ids = {a.id for a in question.answer_options.all()}
            user_answer_options_ids = {a['answer_option'].id for a in user_answer_options}
            check_answer_options = user_answer_options_ids - existing_answer_options_ids
            if check_answer_options:
                raise ValidationError({'ValidationError': 'В запросе присутствуют варианты ответов, не соответствующие '
                                                          f'предложенным в вопросе: {check_answer_options}'})

        return attrs

    def create(self, validated_data):
        user_answer_options = validated_data.get('user_answer_options')
        if user_answer_options is not None:
            validated_data.pop('user_answer_options')
            answer = super().create(validated_data)
            user_answer_options_objs = [UserAnswerOptions(
                answer_option=a['answer_option'], answer=answer
            ) for a in
                user_answer_options
            ]
            UserAnswerOptions.objects.bulk_create(user_answer_options_objs)
            return answer
        return super().create(validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вопросов
    """

    answer_options = QuestionsAnswerOptionsSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'quiz', 'answer_options', ]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request.data.get('type') == 'TEXT':
            fields['answer_options'].required = False
        elif request.data.get('type') in ['SINGLE_QUESTION_OPTION', 'MULTIPLE_QUESTION_OPTION']:
            fields['answer_options'].required = True
        return fields

    def validate(self, attrs):
        question_type = attrs['type'] if self.context['view'].action == 'create' else self.instance.type
        # Валидация по типу вопроса:
        if question_type == 'TEXT':
            try:
                attrs.pop('answer_options')
            except KeyError:
                pass
        elif question_type in ['SINGLE_ANSWER_OPTION', 'MULTIPLE_ANSWER_OPTION']:
            # Валидация answer_options:
            answer_options = attrs['answer_options']
            if len(answer_options) == 0:
                raise ValidationError({'ValidationError': 'Укажите непустое значение для поля "answer_options"'})

            answer_options_set = {a['name'] for a in answer_options}
            if len(answer_options) != len(answer_options_set):
                raise ValidationError({'ValidationError': 'В вариантах ответа содержатся дубли'})

            if self.context['view'].action in ['update', 'partial_update']:
                existing_answer_options = {a.name for a in self.instance.answer_options.all()}
                duplicate_answer_options = existing_answer_options & answer_options_set
                if duplicate_answer_options:
                    raise ValidationError({'ValidationError': f'У вопроса уже есть следующие варианты ответов: '
                                                              f'{sorted(duplicate_answer_options)}'})
        return attrs

    def create(self, validated_data):
        # Обработка вложенного поля answer_options:
        answer_options = validated_data.get('answer_options')
        if answer_options is not None:
            validated_data.pop('answer_options')
            question = super().create(validated_data)
            # Создание связанных сущностей QuestionAnswerOptions:
            answer_options_objs = [
                QuestionAnswerOptions(name=a['name'], question=question)
                for a in answer_options
            ]
            QuestionAnswerOptions.objects.bulk_create(answer_options_objs)
            return question
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Обработка вложенного поля answer_options:
        answer_options = validated_data.get('answer_options')
        if answer_options and instance.type in ['SINGLE_ANSWER_OPTION', 'MULTIPLE_ANSWER_OPTION']:
            # Создание связанных сущностей QuestionAnswerOptions:
            answer_options_objs = [
                QuestionAnswerOptions(name=a['name'], question=instance)
                for a in answer_options
            ]
            QuestionAnswerOptions.objects.bulk_create(answer_options_objs)
        return super().update(instance, validated_data)


class QuestionAnswerSerializer(QuestionSerializer):
    """
    Сериализаторо для вопросов, расширенный информацией с ответами
    """
    answer = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'quiz', 'answer_options', 'answer', ]


class QuizSerializer(serializers.ModelSerializer):
    """
    Сериализатор для опросов. Содержит базовую информацию
    """

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'start_date', 'end_date', 'description', 'questions']

    def validate(self, attrs):
        start_date, end_date = attrs.get('start_date'), attrs.get('end_date')
        # Валидация start_date:
        if start_date:
            if self.context['view'].action in ['update', 'partial_update']:
                raise ValidationError({'ValidationError': 'После создания поле "дата старта" у опроса менять нельзя'})
            if start_date < timezone.localdate():
                raise ValidationError({'ValidationError': 'Дата старта не может быть раньше текущей'})
        # Валидация end_date:
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError({'ValidationError': 'Дата окончания не может быть раньше даты старта'})
        return attrs


class QuizUserAnswerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для опросов, расширенный информацией с вопросами
    """
    questions = QuestionAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'start_date', 'end_date', 'description', 'questions', ]
