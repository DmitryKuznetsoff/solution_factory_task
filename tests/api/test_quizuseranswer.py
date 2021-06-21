import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK


@pytest.mark.django_db
def test_quiz_retrieve_by_user_id(user_api_client, user, quiz_factory, question_factory, answer_factory):
    quiz_list = quiz_factory(_quantity=10)
    [q.questions.set(question_factory(_quantity=10)) for q in quiz_list]
    random_quiz = random.choice(quiz_list)
    [answer_factory(question=q, _quantity=1) for q in random_quiz.questions.all()]
    url = reverse('quizuseranswer-list')

    resp = user_api_client.get(url, {'user': user.id})
    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()
    user_ids = [q['answer'][0]['user'] for q in resp_json[0]['questions']]
    assert all(lambda x: x == user for u in user_ids)
