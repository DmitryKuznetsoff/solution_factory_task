import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_quiz_retrieve(admin_api_client, quiz_factory):
    quiz = quiz_factory()
    url = reverse('quiz-detail', args=[quiz.id])

    resp = admin_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert quiz.id == resp_json['id']


@pytest.mark.django_db
def test_quiz_list(admin_api_client, quiz_factory):
    quiz_list = quiz_factory(_quantity=10)
    url = reverse('quiz-list')

    resp = admin_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    expected_ids = {q.id for q in quiz_list}
    response_ids = {q['id'] for q in resp_json}
    assert expected_ids == response_ids


@pytest.mark.django_db
def test_quiz_create_by_user(user_api_client, quiz_create_payload):
    url = reverse('quiz-list')

    resp = user_api_client.post(url, data=quiz_create_payload, format='json')

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_quiz_create_by_admin(admin_api_client, quiz_create_payload):
    url = reverse('quiz-list')

    resp = admin_api_client.post(url, data=quiz_create_payload, format='json')

    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json['title'] == quiz_create_payload['title']


@pytest.mark.django_db
def test_quiz_update_by_user(user_api_client, quiz_factory):
    quiz = quiz_factory()
    url = reverse('quiz-detail', args=[quiz.id])
    payload = {'title': f'{quiz.title} patched'}

    resp = user_api_client.patch(url, data=payload)

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_quiz_update_by_admin(admin_api_client, quiz_factory):
    quiz = quiz_factory()

    url = reverse('quiz-detail', args=[quiz.id])
    payload = {'title': f'{quiz.id} patched'}

    resp = admin_api_client.patch(url, data=payload)

    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert payload['title'] == resp_json['title']


@pytest.mark.django_db
def test_quiz_delete_by_user(user_api_client, quiz_factory):
    quiz_list = quiz_factory(_quantity=10)
    random_quiz = random.choice(quiz_list)
    url = reverse('quiz-detail', args=[random_quiz.id])

    resp = user_api_client.delete(url)

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_quiz_delete_by_admin(admin_api_client, quiz_factory):
    quiz_list = quiz_factory(_quantity=10)
    random_quiz = random.choice(quiz_list)
    url = reverse('quiz-detail', args=[random_quiz.id])

    resp = admin_api_client.delete(url)

    assert resp.status_code == HTTP_204_NO_CONTENT

    existing_ids = [q['id'] for q in admin_api_client.get(reverse('quiz-list')).json()]
    assert random_quiz.id not in existing_ids
