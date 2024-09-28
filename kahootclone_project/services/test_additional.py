from .test_services import ServiceBaseTest


from django.urls import reverse
from time import sleep

###################
# You may modify the following variables
from models.models import Answer as Answer
from models.models import Game as Game
from models.models import Participant as Participant
from models.models import Guess as Guess

from models.constants import QUESTION, WAITING

# XXX_SERVICE is the alias of the service we want to test
# XXX_KEY is the key, in the context diccionary, with the information
# that we want to pass to the template
# For example response.context['latest_questionnaire_list'] should contain
# the last five questionnaires created by the logged user


QUESTIONNAIRE_LIST_KEY = "questionnaire_list"

ANSWER_CREATE_SERVICE = "answer-create"
ANSWER_UPDATE_SERVICE = "answer-update"

GAME_CREATE_SERVICE = "game-create"

LOGIN_SERVICE = "login"
LOGOUT_SERVICE = "logout"

PARTICIPANT_REMOVE_SERVICE = "participant-remove"

GAME_UPDATE_PARTICIPANT_SERVICE = "game-updateparticipant"
CHECK_ALL_ANSWERED_SERVICE = "check-all-answered"


class ServiceTests(ServiceBaseTest):

    def checkNoLogin(self, SERVICE, KEY, args=None, redirectLoginPage=True):
        """ check key is not in response if user is not logged"""
        # no login, therefore key KEY should be empty
        # first logout just in case
        self.client1.get(reverse(LOGOUT_SERVICE), follow=True)
        if args is None:
            response = self.client1.get(
                reverse(SERVICE), follow=True)
        else:
            response = self.client1.get(
                reverse(SERVICE, args=args), follow=True)
        # check no active user

        self.assertFalse(response.context['user'].is_active)
        # check no latest_questionnaire_list
        self.assertFalse(KEY in response.context)

        # return should be login page
        if redirectLoginPage:
            self.assertIn('username', self.decode(response.content))

        return response

    def checkLogin(self, SERVICE, KEY, args=None):
        """ log in and check key is in response when user is logged"""
        # log-in
        response = self.client1.post(reverse(LOGIN_SERVICE),
                                     self.userDict, follow=True)
        # after login session user should exist
        self.assertTrue(response.context['user'].is_active)
        if args is None:
            response = self.client1.get(
                reverse(SERVICE), follow=True)
        else:
            response = self.client1.get(
                reverse(SERVICE, args=args), follow=True)

        # latest_questionnaire_list should exist
        if KEY != "DO_NOT_CHECK_KEY":
            self.assertTrue(KEY in response.context)

        return response

    def checkLoginSecondPart(self, SERVICE, args, kwargs=None):
        """ for those cases in which there is a confirmation page
        or a form and a post should follow a get request"""
        if kwargs is None:
            response = self.client1.post(
                reverse(SERVICE, args=args), follow=True)
        else:
            response = self.client1.post(
                reverse(SERVICE, args=args), kwargs, follow=True)

        return response

# ===== ANSWER =====
    def test_too_many_answers(self):
        "check too_many_answers"
        # Author: Pablo Cuesta Sierra
        print("test too_many_answers")
        # delete all answers so it is easier to check
        Answer.objects.all().delete()
        id = self.question.id
        args = [str(id)]
        kwargs = {'answer': 'new answer', "correct": False}

        # no login, therefore key should be empty
        # response =
        self.checkNoLogin(ANSWER_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)

        for _ in range(4):
            # login in, two calls are needed because there is an intermediate
            # form  asking for the field 'title'
            # response =
            self.checkLogin(
                ANSWER_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
            # print("RESPONSE", self.decode(response.content))
            # response =
            self.checkLoginSecondPart(
                ANSWER_CREATE_SERVICE, args=args, kwargs=kwargs)

        # print("RESPONSE", self.decode(response.content))
        # questionarie need to be reload, that is,
        # self.questionnarie has old values
        self.assertEqual(Answer.objects.count(), 4)

        self.checkLogin(
            ANSWER_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
        response = self.checkLoginSecondPart(
            ANSWER_CREATE_SERVICE, args=args, kwargs=kwargs)

        self.assertIn(
            "maximum 4 answers per question",
            response.content.decode("utf-8").lower())

        self.assertEqual(Answer.objects.count(), 4)

    def test_update_answer(self):
        "check update_answer"
        # Author: Pablo Cuesta Sierra
        print("test update_answer")

        Answer.objects.all().delete()
        id = self.question.id
        args = [str(id)]
        kwargs = {'answer': 'new answerr', "correct": False}

        self.checkLogin(ANSWER_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
        self.checkLoginSecondPart(
            ANSWER_CREATE_SERVICE, args=args, kwargs=kwargs)

        self.assertEqual(Answer.objects.count(), 1)
        answer = Answer.objects.first()
        args = [str(answer.id)]
        self.checkLogin(ANSWER_UPDATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
        kwargs['answer'] = 'new answer'
        response = self.checkLoginSecondPart(
            ANSWER_UPDATE_SERVICE, args=args, kwargs=kwargs
        )
        self.assertEqual(Answer.objects.count(), 1)
        answer = Answer.objects.first()
        self.assertEqual(answer.answer, kwargs['answer'])

        self.assertTemplateUsed(response, 'models/question_detail.html')

    def test_remove_participant(self):
        "check remove_participant"
        # Author: Álvaro Zamanillo Sáez
        print("test remove_participant")
        # create a game
        id = self.questionnaire.id
        args = [str(id)]
        kwargs = {'state': WAITING}

        # no login, therefore key should be empty
        # response =
        self.checkNoLogin(GAME_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)

        # login in,
        # response =
        self.checkLogin(GAME_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
        # print("RESPONSE", self.decode(response.content))
        game = Game.objects.first()
        self.assertEqual(game.questionnaire.id, int(id))
        self.assertEqual(game.state, kwargs["state"])
        # create participant and check that appear in the web page
        args = [str(game.publicId)]

        for id in range(10):
            Participant.objects.create(game=game, alias="alias_%d" % id)
            response = self.client1.get(
                reverse(GAME_UPDATE_PARTICIPANT_SERVICE), follow=True)
            for participant in range(id + 1):
                # print("checking participant", "alias_%d" % participant)
                self.assertNotEqual(
                    self.decode(
                        response.content).find("alias_%d" % participant), -1)
            sleep(0.1)

        # remove participant and check that disappear in the web page
        for id in range(10):
            alias = "alias_%d" % id
            response = self.client1.get(
                reverse(PARTICIPANT_REMOVE_SERVICE, args=[alias]), follow=True)

            # check it has been deleted from database
            self.assertEqual(Participant.objects.filter(
                alias=alias).count(), 0)

            # check it has been deleted from web page
            response = self.client1.get(
                reverse(GAME_UPDATE_PARTICIPANT_SERVICE), follow=True)
            self.assertEqual(
                self.decode(
                    response.content).find(alias), -1)

            # check the others are still there
            for participant in range(id + 1, 10):
                # print("checking participant", "alias_%d" % participant)
                self.assertNotEqual(
                    self.decode(
                        response.content).find("alias_%d" % participant), -1)
            sleep(0.1)

    def test_all_participants_have_answered(self):
        "check all_participants_have_answered"
        # Author: Álvaro Zamanillo Sáez
        print("test all_participants_have_answered")
        # create a game
        id = self.questionnaire.id
        args = [str(id)]

        # no login, therefore key should be empty
        # response =
        self.checkNoLogin(GAME_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)

        # form  asking for the field 'title'
        # response =
        response = self.checkLogin(
            GAME_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
        game = Game.objects.first()

        p1 = Participant.objects.create(
            game=game, alias="alias_1")
        p2 = Participant.objects.create(
            game=game, alias="alias_2")

        game.state = QUESTION
        game.questionNo = 0

        Guess.objects.create(
            participant=p1,
            question=self.question,
            game=game,
            answer=self.answer,)

        self.assertTrue(
            self.decode(
                response.content).find("True"), -1)

        Guess.objects.create(
            participant=p2,
            question=self.question,
            game=game,
            answer=self.answer)

        response = self.client1.get(
            reverse(CHECK_ALL_ANSWERED_SERVICE), follow=True
        )

        self.assertFalse(
            self.decode(
                response.content).find("True"), -1)
