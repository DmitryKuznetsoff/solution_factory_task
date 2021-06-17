from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, QuestionViewSet, AnswerViewSet, QuizUserAnswerViewSet

router = DefaultRouter()
router.register('quiz', QuizViewSet, 'quiz')
router.register('question', QuestionViewSet, 'question')
router.register('answer', AnswerViewSet, 'answer')
router.register('quizuseranswer', QuizUserAnswerViewSet, 'quizuseranswer')

urlpatterns = [
    path('', include(router.urls))
]
