from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    # questionnaire paths
    path(
        'questionnaire/<int:pk>',
        views.QuestionnaireDetailView.as_view(),
        name='questionnaire-detail'
    ),
    path(
        'questionnairelist/',
        views.QuestionnaireListView.as_view(),
        name='questionnaire-list'
    ),
    path(
        'questionnaireremove/<int:pk>/',
        views.QuestionnaireDelete.as_view(),
        name='questionnaire-remove'
    ),
    path(
        'questionnaireupdate/<int:pk>/',
        views.QuestionnaireUpdate.as_view(),
        name='questionnaire-update'
    ),
    path(
        'questionnairecreate/',
        views.QuestionnaireCreate.as_view(),
        name='questionnaire-create'
    ),

    # question paths
    path(
        'question/<int:pk>',
        views.QuestionDetailView.as_view(),
        name='question-detail'
    ),
    path(
        'questionremove/<int:pk>/',
        views.QuestionDelete.as_view(),
        name='question-remove'
    ),
    path(
        'questionupdate/<int:pk>/',
        views.QuestionUpdate.as_view(),
        name='question-update'
    ),
    path(
        'questioncreate/<int:questionnaireid>/',
        views.QuestionCreate.as_view(),
        name='question-create'
    ),


    # answer paths
    path(
        'answerremove/<int:pk>/',
        views.AnswerDelete.as_view(),
        name='answer-remove'
    ),
    path(
        'answerupdate/<int:pk>/',
        views.AnswerUpdate.as_view(),
        name='answer-update'
    ),
    path(
        'answercreate/<int:questionid>/',
        views.AnswerCreate.as_view(),
        name='answer-create'
    ),

    # game paths
    path(
        'gamecreate/<int:questionnaireid>/',
        views.GameCreate.as_view(),
        name='game-create'
    ),
    path(
        'gamecountdown/',
        views.GameCountdown.as_view(),
        name='game-countdown'
    ),
    path(
        'gameUpdateParticipant/',
        views.GameUpdateParticipant.as_view(),
        name='game-updateparticipant'
    ),
    path(
        'participantremove/<str:alias>/',
        views.deleteParticipant,
        name='participant-remove'
    ),
    path(
        'checkAllAnswered/',
        views.checkAllAnswered,
        name='check-all-answered'
    )
]
