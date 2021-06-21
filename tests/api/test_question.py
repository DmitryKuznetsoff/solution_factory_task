import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_question_retrieve(admin_api_client, question_factory):
    question = question_factory()
    url = reverse('question-detail', args=[question.id])

    resp = admin_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert question.id == resp_json['id']


@pytest.mark.django_db
def test_question_list(admin_api_client, question_factory):
    question_list = question_factory(_quantity=10)
    url = reverse('question-list')

    resp = admin_api_client.get(url)
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    expected_ids = {q.id for q in question_list}
    response_ids = {q['id'] for q in resp_json}
    assert expected_ids == response_ids


@pytest.mark.django_db
def test_question_create_by_user(user_api_client, question_create_payload):
    url = reverse('question-list')

    resp = user_api_client.post(url, data=question_create_payload, format='json')

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_text_question_create_by_admin(admin_api_client, question_create_payload):
    url = reverse('question-list')
    question_create_payload.update({'type': 'TEXT'})

    resp = admin_api_client.post(url, data=question_create_payload, format='json')

    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json['text'] == question_create_payload['text']


@pytest.mark.django_db
def test_single_answer_option_question_create_by_admin(admin_api_client, question_create_payload,
                                                       question_answer_options_payload):
    url = reverse('question-list')
    payload = question_create_payload
    payload.update({'type': 'SINGLE_ANSWER_OPTION'}, **question_answer_options_payload)

    resp = admin_api_client.post(url, data=payload, format='json')

    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json['text'] == question_create_payload['text']


@pytest.mark.django_db
def test_multiple_answer_option_question_create_by_admin(admin_api_client, question_create_payload,
                                                         question_answer_options_payload):
    url = reverse('question-list')
    payload = question_create_payload
    payload.update({'type': 'MULTIPLE_ANSWER_OPTION'}, **question_answer_options_payload)

    resp = admin_api_client.post(url, data=payload, format='json')

    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json['text'] == question_create_payload['text']


@pytest.mark.django_db
def test_question_update_by_user(user_api_client, question_factory):
    question = question_factory()

    url = reverse('question-detail', args=[question.id])
    payload = {'text': f'{question.text} patched'}

    resp = user_api_client.patch(url, data=payload)

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_question_update_by_admin(admin_api_client, question_factory):
    question = question_factory()

    url = reverse('question-detail', args=[question.id])
    payload = {'text': f'patched'}

    resp = admin_api_client.patch(url, data=payload)

    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    assert payload['text'] == resp_json['text']


@pytest.mark.django_db
def test_question_delete_by_user(user_api_client, question_factory):
    random_question = random.choice(question_factory(_quantity=10))
    url = reverse('question-detail', args=[random_question.id])

    resp = user_api_client.delete(url)

    assert resp.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_question_delete_by_admin(admin_api_client, question_factory):
    random_question = random.choice(question_factory(_quantity=10))
    url = reverse('question-detail', args=[random_question.id])

    resp = admin_api_client.delete(url)

    assert resp.status_code == HTTP_204_NO_CONTENT

    existing_ids = [q['id'] for q in admin_api_client.get(reverse('question-list')).json()]
    assert random_question.id not in existing_ids
