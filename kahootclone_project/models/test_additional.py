from django.test import TestCase
from django.forms import ValidationError
from django.urls import reverse

###################
from .models import (
    User, Questionnaire, Question, Answer, Game, Participant, Guess
)
from .models import MAX_PUBLICID
from .constants import (WAITING, QUESTION, ANSWER, LEADERBOARD)

###################

NUMBERUSERS = 3
USER_SESSION_ID = "_auth_user_id"
HOME_PAGE = "home"


class ModelAdditionalTests(TestCase):
    """Test the models"""
    # Author: Pablo Cuesta Sierra

    def setUp(self):
        "create basic objects for the tests"
        # Author: Pablo Cuesta Sierra
        self.user = User.objects.create(
            username="__test_additional", password="__test_additional")
        self.questionnaire = Questionnaire.objects.create(
            title="__test_additional", user=self.user)

        self.question = Question.objects.create(
            question="__test_additional",
            questionnaire=self.questionnaire,
            answerTime=10)

        self.question2 = Question.objects.create(
            question="__test_additional2",
            questionnaire=self.questionnaire,
            answerTime=10)

        self.answer = Answer.objects.create(
            answer="__test_additional",
            question=self.question,
            correct=True)

        self.game = Game.objects.create(
            questionnaire=self.questionnaire)

    def test_get_owner(self):
        # Author: Pablo Cuesta Sierra
        print("test get_owner")
        self.assertEqual(self.questionnaire.get_owner(), self.user)
        self.assertEqual(self.question.get_owner(), self.user)
        self.assertEqual(self.answer.get_owner(), self.user)
        self.assertEqual(self.game.get_owner(), self.user)

    def test_get_absolute_url(self):
        # Author: Pablo Cuesta Sierra
        print("test get_absolute_url")
        self.assertEqual(
            self.questionnaire.get_absolute_url(),
            f"/services/questionnaire/{self.questionnaire.id}"
        )
        self.assertEqual(
            self.question.get_absolute_url(),
            f"/services/question/{self.question.id}"
        )

    def test_max_publicid(self):
        # Author: Pablo Cuesta Sierra
        print("test max_publicid")

        # create the max number of games possible
        create_num = MAX_PUBLICID - Game.objects.count()
        for _ in range(create_num):
            Game.objects.create(questionnaire=self.questionnaire)

        self.assertRaises(  # another creation should fail
            ValidationError,
            Game.objects.create,
            questionnaire=self.questionnaire,
        )

        for _ in range(create_num):
            Game.objects.last().delete()

    def test_game_state(self):
        # Author: Pablo Cuesta Sierra
        print("test game_state")

        questionnaire = Questionnaire.objects.create(
            title="__test_additional_game_state", user=self.user)

        num_questions = 10
        for i in range(num_questions):
            Question.objects.create(
                question=f'q{i}',
                questionnaire=questionnaire,
                answerTime=10 + i,
            )

        # we now check every possible state of the game with 10 questions
        game = Game.objects.create(questionnaire=questionnaire)
        self.assertEqual(game.state, WAITING)

        for i in range(num_questions):
            game.update_state()
            self.assertEqual(game.state, QUESTION)
            self.assertEqual(game.questionNo, i)
            self.assertEqual(game.countdownTime, 10 + i)
            game.update_state()
            self.assertEqual(game.state, ANSWER)
            self.assertEqual(game.questionNo, i)

        game.update_state()
        self.assertEqual(game.state, LEADERBOARD)
        game.update_state()  # this state should not change anymore
        self.assertEqual(game.state, LEADERBOARD)
        game.update_state()
        self.assertEqual(game.state, LEADERBOARD)

    def test_repeated_alias(self):
        # Author: Pablo Cuesta Sierra
        print("test repeated_alias")
        repeated_alias = "__alias"
        game = Game.objects.create(questionnaire=self.questionnaire)
        Participant.objects.create(game=game, alias=repeated_alias)
        # creation of participant with same alias should fail
        self.assertRaises(
            ValidationError,
            Participant.objects.create,
            game=game,
            alias=repeated_alias,
        )

    def test_invalid_creation_or_update(self):
        # Author: Álvaro Zamanillo Sáez

        print("test invalid_creation_or_update")

        # Try to create another correct answer
        with self.assertRaises(ValidationError):
            Answer.objects.create(
                answer="",
                question=self.question,
                correct=True)

        answer = Answer.objects.create(
            answer="",
            question=self.question,
            correct=False)

        # Try to modify an answer to correct when there is already
        # one correct answer.
        with self.assertRaises(ValidationError):
            answer.correct = True
            answer.save()

    def test_is_saved_as_correct(self):
        # Author: Álvaro Zamanillo Sáez

        print("test is_saved_as_correct")

        self.assertTrue(self.answer._is_saved_as_correct())

        answer = Answer.objects.create(
            answer="",
            question=self.question,
            correct=False)

        self.assertFalse(answer._is_saved_as_correct())

    def test_edit_guess(self):
        # Author: Pablo Cuesta Sierra
        print("test edit_guess")
        answer2 = Answer.objects.create(
            answer="__test_additional2",
            question=self.question,
            correct=False
        )
        game = Game.objects.create(questionnaire=self.questionnaire)
        participant = Participant.objects.create(game=game, alias="__alias")
        game.state = QUESTION  # for the guess to be accepted
        guess = Guess.objects.create(
            participant=participant,
            question=self.question,
            answer=self.answer,
            game=game,
        )

        exception = False
        try:
            guess.answer = answer2
            guess.save()
        except ValidationError:
            exception = True
        self.assertTrue(exception)

    def test_making_late_guess(self):
        # Author: Álvaro Zamanillo Sáez
        print("test making late guess")
        game = Game.objects.create(questionnaire=self.questionnaire)
        participant = Participant.objects.create(game=game, alias="__alias")
        exception = False

        game.state = QUESTION
        game.questionNo = 1
        game.save()

        past_question = Question.objects.filter(
            questionnaire=self.questionnaire).first()
        current_question = Question.objects.filter(
            questionnaire=self.questionnaire).last()

        # Try to guess question 1 while the questionnaire is in question 2
        try:
            Guess.objects.create(
                participant=participant,
                question=past_question,
                answer=self.answer,
                game=game,
            )
        except ValidationError:
            exception = True
        self.assertTrue(exception)

        # Try to guess question 2 while the questionnaire is in question 2
        exception = False
        try:
            Guess.objects.create(
                participant=participant,
                question=current_question,
                answer=self.answer,
                game=game,
            )
        except ValidationError:
            exception = True
        self.assertFalse(exception)

    def test_all_participants_have_answered(self):
        # Author: Álvaro Zamanillo Sáez
        print("test all participants have answered")

        # create two participants for the game
        p1 = Participant.objects.create(game=self.game, alias="__alias1")
        p2 = Participant.objects.create(game=self.game, alias="__alias2")

        # set the game state to question to allow guesses
        self.game.questionNo = 0
        self.game.state = QUESTION

        # participant 1 makes a guess
        Guess.objects.create(
            participant=p1,
            question=self.question,
            answer=self.answer,
            game=self.game,
        )

        self.assertFalse(self.game.all_participants_answered())

        # participant 2 makes a guess
        Guess.objects.create(
            participant=p2,
            question=self.question,
            answer=self.answer,
            game=self.game,
        )

        self.assertTrue(self.game.all_participants_answered())

    def test_too_many_answers(self):
        # Author: Pablo Cuesta Sierra
        print("test too_many_answers")
        question = Question.objects.create(
            question="__question",
            questionnaire=self.questionnaire,
        )

        # create 4 answers
        for i in range(0, 4):
            Answer.objects.create(
                answer="__answer_%d" % i,
                question=question,
                correct=False
            )

        # try to create one more answer
        self.assertRaises(
            ValidationError,
            Answer.objects.create,
            answer="__answer_4",
            question=question,
            correct=False
        )


class ModelViewsAdditionalTests(TestCase):
    # Author: Pablo Cuesta Sierra
    def setUp(self):
        User.objects.all().delete()
        self.usersList = []
        self.users = []
        for i in range(0, NUMBERUSERS):
            user = {"username": "user_%d" % i,
                    "password": "password_%d" % i,
                    "first_name": "name_%d" % i,
                    "last_name": "last_%d" % i,
                    "email": "email_%d@gmail.com" % i}
            self.usersList.append(user)
            user = User.objects.create_user(**user)

            # store user id in list
            self.usersList[i]["id"] = user.id
            self.users.append(user)

    def test_get_signup(self):
        # Author: Pablo Cuesta Sierra
        print("test get_signup")
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_post_signup_bad_form(self):
        # Author: Pablo Cuesta Sierra
        print("test post_signup_bad_form")
        user = self.usersList[0]
        password = 'gjgjhgkjjgjggjhg'
        # try to create existing user:
        response = self.client.post(
            reverse("signup"),
            {
                "username": user["username"],
                "password1": password,
                "password2": password,
            },
            follow=True,
        )
        # again, we should be redirected to the signup, as user already exists
        self.assertTemplateUsed(response, "registration/signup.html")
        self.assertTrue("already exists" in response.content.decode('utf-8'))
