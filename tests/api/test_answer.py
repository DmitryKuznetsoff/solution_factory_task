import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED


@pytest.mark.django_db
def test_answer_retrieve(user_api_client, answer_factory):
    answer = answer_factory()
    url = reverse('answer-detail', args=[answer.id])

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert answer.id == resp_json['id']


@pytest.mark.django_db
def test_answer_list(user_api_client, answer_factory):
    answer_list = answer_factory(_quantity=10)
    url = reverse('answer-list')

    resp = user_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    expected_ids = {a.id for a in answer_list}
    response_ids = {a['id'] for a in resp_json}
    assert expected_ids == response_ids


@pytest.mark.django_db
def test_text_answer_create(user_api_client, question_factory):
    url = reverse('answer-list')
    question = question_factory()
    payload = {
        'question': question.id,
        'text': 'something'
    }

    resp = user_api_client.post(url, data=payload, format='json')
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json['text'] == payload['text']


@pytest.mark.django_db
def test_single_answer_option_create(user_api_client, question_factory, question_answer_options_factory):
    url = reverse('answer-list')

    question = question_factory(type='SINGLE_ANSWER_OPTION')
    question.answer_options.set(question_answer_options_factory(_quantity=10))
    user_answer = random.choice(question.answer_options.all())
    payload = {
        'question': question.id,
        'user_answer_options':
            [
                {'answer_option': user_answer.id}
            ]
    }

    resp = user_api_client.post(url, data=payload, format='json')
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json['user_answer_options'] == payload['user_answer_options']


@pytest.mark.django_db
def test_multiple_answer_option_post(user_api_client, question_factory, question_answer_options_factory):
    url = reverse('answer-list')

    question = question_factory(type='MULTIPLE_ANSWER_OPTION')
    question.answer_options.set(question_answer_options_factory(_quantity=10))
    user_answers = random.sample(list(question.answer_options.all()), 3)
    payload = {
        'question': question.id,
        'user_answer_options': [{'answer_option': a.id} for a in user_answers]
    }

    resp = user_api_client.post(url, data=payload, format='json')
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json['user_answer_options'] == payload['user_answer_options']
