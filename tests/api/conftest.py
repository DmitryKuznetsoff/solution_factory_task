import datetime

import pytest
from django.utils.timezone import localdate
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


# Общие фикстуры для api

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='user', password='password')


@pytest.fixture
def user_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def user_api_client(user_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
    return client


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create(username='admin', password='password', is_staff=True)


@pytest.fixture
def admin_token(admin):
    token, _ = Token.objects.get_or_create(user=admin)
    return token


@pytest.fixture
def admin_api_client(admin_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token}')
    return client


# Фикстуры для тестов quiz:

@pytest.fixture
def quiz_factory():
    def factory(*args, **kwargs):
        return baker.make('Quiz', *args, **kwargs, )

    return factory


@pytest.fixture
def quiz_create_payload():
    start_date = localdate()
    end_date = localdate() + datetime.timedelta(days=1)

    return {
        "title": "quiz1",
        "start_date": start_date,
        "end_date": end_date,
        "description": "quiz1_description"
    }


# Фикстуры для тестов question

@pytest.fixture
def question_factory():
    def factory(*args, **kwargs):
        return baker.make('Question', *args, **kwargs)

    return factory


@pytest.fixture
def question_create_payload(quiz_factory):
    quiz = quiz_factory(_quantity=1)[0]
    return {
        "text": "something",
        "quiz": quiz.id
    }


@pytest.fixture
def question_answer_options_payload():
    return {
        'answer_options':
            [
                {'name': 'option#1'},
                {'name': 'option#2'},
                {'name': 'option#3'}
            ]
    }


@pytest.fixture
def question_answer_options_factory():
    def factory(*args, **kwargs):
        return baker.make('QuestionAnswerOptions', *args, **kwargs)

    return factory


# Фикстуры для тестов answer

@pytest.fixture
def answer_factory(user):
    def factory(*args, **kwargs):
        return baker.make('Answer', user=user, *args, **kwargs)

    return factory
