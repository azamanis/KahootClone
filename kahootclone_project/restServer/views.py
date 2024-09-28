from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
import rest_framework.permissions as permissions

from models.constants import WAITING
from models.models import Participant, Game, Guess
from restServer.serializer import (
    ParticipantSerializer, GameSerializer, GuessSerializer
)


# ------------------ USEFUL RESPONSES ------------------

RESPONSE_GAME_WAITING = Response(
    "This game is not accepting participants",
    status=status.HTTP_403_FORBIDDEN
)


def RESPONSE_PARTICIPANT_NONE_VALUES(id, alias, game):
    ''' Response used when the input of a Participant
        creation is wrong or missing a value.
    '''
    # Author: Pablo Cuesta Sierra
    return Response(
        ("Some value is None: "
         f"{'{'}id:{id}, alias:{alias}, game:{game}{'}'}"),
        status=status.HTTP_400_BAD_REQUEST
    )


def RESPONSE_GUESS_NONE_VALUES(
    gameId, participantId, answer, game, participant
):
    ''' Response used when the input of a Guess
        creation is wrong or missing a value.
    '''
    # Author: Pablo Cuesta Sierra
    return Response((
        f"Some value is None: {'{'}gameId:{gameId}, "
        f"participantId:{participantId}, "
        f"answer:{answer}, "
        f"game:{game}, "
        f"participant:{participant}{'}'}"
    ),
        status=status.HTTP_400_BAD_REQUEST)


def RESPONSE_METHOD_NOT_ALLOWED(msg=None):
    ''' Response used to indicate that a method is not allowed.
        msg: optional message for the response
    '''
    # Author: Pablo Cuesta Sierra
    return Response(
        f"This method is not allowed{f': {msg}' if msg else '.'}",
        status=status.HTTP_403_FORBIDDEN
    )


# ------------------ PERMISSION CLASSSES ------------------


class PostPermission(permissions.BasePermission):
    '''
    Permission class that allows only creation operations (POST requests).
    '''
    # Author: Álvaro Zamanillo Sáez

    def has_permission(self, request, view):
        return (request.method == 'POST')


# ------------------ VIEWSETS ------------------


class GameView(viewsets.ModelViewSet):
    ''' API endpoint that returns the Game object associated to a publicId.
        Input: publicId
        Output: game object serialized as a json.
    '''
    # Author: Álvaro Zamanillo Sáez

    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'publicId'

    def list(self, request, *args, **kwargs):
        # Author: Pablo Cuesta Sierra
        return RESPONSE_METHOD_NOT_ALLOWED((
            'Not possible to list all games for privacy issues. '
            'Players must specify the publicId of the game they want to join.'
        ))


class ParticipantViewSet(viewsets.ModelViewSet):
    ''' API endpoint that allows Game's Participants to be created.
        Input: {'game': int, 'alias': string}
    '''
    # Author: Álvaro Zamanillo Sáez

    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    def get_permissions(self):
        return [PostPermission()]

    def create(self, request, *args, **kwargs):
        ''' Creates a participant given a publicId and a alias. '''

        alias = request.data.get('alias', None)
        try:
            gameId = request.data.get('game', None)
            game = Game.objects.get(publicId=gameId)
        except Game.DoesNotExist:
            game = None

        values = (gameId, alias, game)
        if None in values:
            return RESPONSE_PARTICIPANT_NONE_VALUES(*values)

        if game.state != WAITING:
            return RESPONSE_GAME_WAITING

        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(e, status=status.HTTP_403_FORBIDDEN)


class GuessViewSet(viewsets.ModelViewSet):
    ''' API endpoint that allows Game's Participants to create Guesses.
        Input: {game: int, uuidp:string, answer:int}.
        Only allows creation.
    '''
    # Author: Álvaro Zamanillo Sáez

    queryset = Guess.objects.all()
    lookup_field = 'pk'  # pk instead uuidP because of test delete_guess
    serializer_class = GuessSerializer

    def get_permissions(self):
        return [PostPermission()]

    def create(self, request, *args, **kwargs):

        # get input data
        gameId = request.data.get('game', None)
        participantId = request.data.get('uuidp', None)
        answerIndex = request.data.get('answer', None)

        try:
            game = Game.objects.get(publicId=gameId)
        except Game.DoesNotExist:
            game = None
        try:
            participant = Participant.objects.get(uuidP=participantId)
        except (Participant.DoesNotExist, ValidationError):
            participant = None

        values = (gameId, participantId, answerIndex, game, participant)
        if None in values or (participant.game != game):
            return RESPONSE_GUESS_NONE_VALUES(*values)

        # get the current question of the game
        question = game.questionnaire.question_set.all()[game.questionNo]
        try:
            # the guess creation takes care of the repeated guesses validation
            guess = Guess.objects.create(
                game=game,
                participant=participant,
                question=question,
                answer=question.answer_set.all()[int(answerIndex)]
            )
        except ValidationError as e:
            return Response(e, status=status.HTTP_403_FORBIDDEN)
        except IndexError:
            return Response(
                "Invalid guess", status=status.HTTP_400_BAD_REQUEST
            )

        serialized_guess = self.serializer_class(guess).data
        return Response(serialized_guess, status=status.HTTP_201_CREATED)


# Create your views here.


# IMPORTANTE: Usar viewset.ModelViewSet para todo

# class MyModelViewSet(viewsets.ModelViewSet):
#     queryset = MyModel.objects.all()
#     serializer_class = MyModelSerializer

#     def list(self, request, *args, **kwargs):
#         # Code to handle GET (list) request
#         pass

#     def create(self, request, *args, **kwargs):
#         # Code to handle POST (create) request
#         pass

#     def retrieve(self, request, *args, **kwargs):
#         # Code to handle GET (retrieve) request
#         pass

#     def update(self, request, *args, **kwargs):
#         # Code to handle PUT (update) request
#         pass

#     def partial_update(self, request, *args, **kwargs):
#         # Code to handle PATCH (partial update) request
#         pass

#     def destroy(self, request, *args, **kwargs):
#         # Code to handle DELETE (destroy) request
#         pass


# class GetAndPostPermission(permissions.BasePermission):
#     '''
#     Permission class that allows only creation operations and retrieving.
#     '''

#     def has_permission(self, request, view):
#         return request.method == 'POST' or request.method == 'GET'
