# Author: Pablo Cuesta Sierra <pablo.cuestas@estudiante.uam.es>

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from models.models import (
    Game, Guess, Participant, User, Questionnaire, Question, Answer)
from rest_framework.reverse import reverse
from models.constants import QUESTION, WAITING, ANSWER, LEADERBOARD
###################
# You may modify the following variables
#     default API names
#     URL Style           HTTP Method	Action	       alias
#     {prefix}/           GET	        list	       {basename}-list
#                         POST	        create
#     {prefix}/{lookup}/  GET	        retrieve	   {basename}-detail
#                         PUT	        update
#                         PATCH	        partial_update
#                         DELETE	    destroy
# rest API service alias


GAME_DETAIL = "game-detail"
GAME_LIST = "game-list"

PARTICIPANT_DETAIL = "participant-detail"
PARTICIPANT_LIST = "participant-list"

GUESS_DETAIL = "guess-detail"
GUESS_LIST = "guess-list"


# these are the error messages returned by the application in
# different contexts.
GUESS_ERROR = 'Wait until the question is shown'
GUESS_DELETE_ERROR = "Authentication credentials were not provided."
GUESS_UPDATE_ERROR = "Authentication credentials were not provided."
GUESS_CREATE_ERROR = "Authentication credentials were not provided."

PARTICIPANT_UPDATE_ERROR = "Authentication credentials were not provided."
PARTICIPANT_DELETE_ERROR = "Authentication credentials were not provided."
PARTICIPANT_LIST_ERROR = "Authentication credentials were not provided."

GAME_NOT_WAITING_ERROR = "This game is not accepting participants"


#####################################################


class RestAdditionalTests(APITestCase):
    """ additional tests for the rest framework seeking full coverage
    """

    def setUp(self):
        # ApiClient acts as a dummy web browser, allowing you to test your
        # views and interact with your Django application programmatically.
        self.client = APIClient()
        # create user
        self.userDict = {"username": 'a',
                         "password": 'a',
                         "first_name": 'a',
                         "last_name": 'a',
                         "email": 'a@aa.es'}
        user, created = User.objects.get_or_create(**self.userDict)
        # save password encripted
        if created:
            user.set_password(self.userDict['password'])
            user.save()
        self.user = user

        # create questionnaire
        self.questionnaireDict = {"title": 'questionnaire_title',
                                  "user": self.user}
        self.questionnaire = Questionnaire.objects.get_or_create(
            **self.questionnaireDict)[0]

        # create a few questions
        # question 1
        self.questionDict = {"question": 'this is a question',
                             "questionnaire": self.questionnaire}
        self.question = Question.objects.get_or_create(**self.questionDict)[0]

        # question2
        self.questionDict2 = {"question": 'this is a question2',
                              "questionnaire": self.questionnaire}
        self.question2 = Question.objects.get_or_create(
            **self.questionDict2)[0]

        # create a few answers
        # answer1
        self.answerDict = {"answer": 'this is an answer',
                           "question": self.question,
                           "correct": True}
        self.answer = Answer.objects.get_or_create(**self.answerDict)[0]

        # answer2
        self.answerDict2 = {"answer": 'this is an answer2',
                            "question": self.question,
                            "correct": False}
        self.answer2 = Answer.objects.get_or_create(**self.answerDict2)[0]

        # answer3
        self.answerDict3 = {"answer": 'this is an answer3',
                            "question": self.question2,
                            "correct": True}
        self.answer3 = Answer.objects.get_or_create(**self.answerDict3)[0]

        # create a game
        self.gameDict = {
            'questionnaire': self.questionnaire,
            'publicId': 123456}
        self.game = Game.objects.get_or_create(**self.gameDict)[0]

        # create a participant
        self.participantDict = {
            'game': self.game,
            'alias': "pepe"}
        self.participant = Participant.objects.get_or_create(
            **self.participantDict)[0]

        # create a guess
        self.guessDict = {
            'participant': self.participant,
            'game': self.game,
            'question': self.question,
            'answer': self.answer}

        self.game.state = QUESTION
        self.game.save()
        self.guess = Guess.objects.get_or_create(**self.guessDict)[0]
        self.game.state = WAITING
        self.game.save()

    @classmethod
    def decode(cls, txt):
        """convert the html return by the client in something that may
           by printed on the screen"""
        return txt.decode("utf-8")

    def set_current_url(self, url):
        # Author: Pablo Cuesta Sierra
        self.current_url = url

    def assert_status_in_creation_request(
        self,
        msg,
        data,
        expected_status_code=status.HTTP_400_BAD_REQUEST
    ):
        """ Tries to create an object using the POST method
            on the provided self.current_url (see self.set_current_url()).
        Args:
            msg: str to be displayed when assert fails.
            data: dict for the creation request.
            expected_satus_code: response's expected status code for
                                 the test to pass.
        Return: the response of the post request.
        """
        # Author: Pablo Cuesta Sierra

        response = self.client.post(
            path=self.current_url, data=data, format='json')
        self.assertEqual(
            response.status_code,
            expected_status_code,
            msg + '\nResponse data: ' + self.decode(response.content))
        return response

    # ==== GAME ====
    def test015_get_all_games(self):
        " get detail of all games (should not be allowed) "

        url = reverse(GAME_LIST)

        response = self.client.get(path=url, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            ("Listing all games should not be allowed. "
             "A game's information should only be accessd when "
             "knowing its pulicId.")
        )

    # ==== PARTICIPANT ====
    def test025_add_participant_with_missing_values(self):
        " add participant with missing values "
        # Author: Pablo Cuesta Sierra

        self.set_current_url(reverse(PARTICIPANT_LIST))

        # missing alias
        self.assert_status_in_creation_request(
            msg="Participant creation should require an alias",
            data={'game': self.gameDict['publicId']},
        )

        # missing game
        self.assert_status_in_creation_request(
            msg="Participant creation should require a game id",
            data={'alias': "luis"},
        )

        # game with provided id does not exist
        self.assert_status_in_creation_request(
            msg=(
                "Participant creation should require a *valid* game id. "
                "This means that the game id provided has to belong to "
                "some game."
            ),
            data={'game': 1, 'alias': "luis"},
        )

    def test026_add_participant_when_game_not_waiting(self):
        " add participant when game is not waiting "
        # Author: Pablo Cuesta Sierra

        self.set_current_url(reverse(PARTICIPANT_LIST))

        for invalid_state in {QUESTION, ANSWER, LEADERBOARD}:
            self.game.state = invalid_state
            self.game.save()

            self.assert_status_in_creation_request(
                msg=("Participants should not be added if game "
                     "is not WAITING. "
                     f"Game is currently in state: {invalid_state}."),
                data={'game': self.gameDict['publicId'], 'alias': "luis"},
                expected_status_code=status.HTTP_403_FORBIDDEN
            )

        # finally, try to create the participant when the game is
        # actually waiting to make sure the data is correct.
        self.game.state = WAITING
        self.game.save()
        self.assert_status_in_creation_request(
            msg=("Participants should be added if game "
                 "is WAITING. Game is currently in state: WAITING."),
            data={'game': self.gameDict['publicId'], 'alias': "luis"},
            expected_status_code=status.HTTP_201_CREATED
        )

    # ==== GUESS ===
    def test_035_add_guess_with_missing_values(self):
        " add a guess with missing (or invalid) values "
        # Author: Pablo Cuesta Sierra

        self.set_current_url(reverse(GUESS_LIST))

        self.game.questionNo = self.game.questionNo + 1
        self.game.state = QUESTION
        self.game.save()

        # missing uuidp
        self.assert_status_in_creation_request(
            msg="Guess creation should require an uuidp",
            data={'game': self.gameDict['publicId'], 'answer': 0}
        )

        # missing game
        self.assert_status_in_creation_request(
            msg="Guess creation should require a game id",
            data={'uuidp': self.participant.uuidP,
                  'answer': 0}
        )

        # missing valid game
        self.assert_status_in_creation_request(
            msg="Guess creation should require a valid game id",
            data={'uuidp': self.participant.uuidP,
                  'game': 1,
                  'answer': 0}
        )

        # invlid answer index
        self.assert_status_in_creation_request(
            msg="Guess creation should require a valid answer index",
            data={'uuidp': self.participant.uuidP,
                  'game': self.gameDict['publicId'],
                  'answer': 5}
        )

        # invlid uuidp
        self.assert_status_in_creation_request(
            msg="Guess creation should require a valid answer index",
            data={'uuidp': 'asdf',
                  'game': self.gameDict['publicId'],
                  'answer': 0}
        )
