# Populate database
# This file has to be placed within the
# catalog/management/commands directory in your project.
# If that directory doesn't exist, create it.
# The name of the script is the name of the custom command,
# that is, populate.py.
#
# execute python manage.py  populate
#
# use module Faker generator to generate data
# (https://zetcode.com/python/faker/)
import os

from django.core.management.base import BaseCommand
from models.models import Questionnaire as Questionnaire
from models.models import Question as Question
from models.models import Answer as Answer
from models.models import Game as Game
from models.models import Participant as Participant
from models.models import Guess as Guess

from faker import Faker

from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


# The name of this class is not optional must be Command
# otherwise manage.py will not process it properly
class Command(BaseCommand):
    # helps and arguments shown when command python manage.py help populate
    # is executed.
    help = """populate kahootclone database
           """
    # if you want to pass an argument to the function
    # uncomment this line
    # def add_arguments(self, parser):
    #    parser.add_argument('publicId',
    #        type=int,
    #        help='game the participants will join to')
    #    parser.add_argument('sleep',
    #        type=float,
    #        default=2.,
    #        help='wait this seconds until inserting next participant')

    def __init__(self, sneaky=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # "if 'RENDER'" allows you to deal with different
        # behaviour in render.com and locally
        # That is, we check a variable ('RENDER')
        # that is only defined in render.com
        if 'RENDER' in os.environ:
            pass
        else:
            pass

        self.NUMBERUSERS = 4
        self.NUMBERQESTIONARIES = 30
        self.NUMBERQUESTIONS = 100
        self.NUMBERPARTICIPANTS = 20
        self.NUMBERANSWERPERQUESTION = 4
        self.NUMBERGAMES = 4

    # handle is another compulsory name, do not change it"
    # handle function will be executed by 'manage populate'
    def handle(self, *args, **kwargs):
        "this function will be executed by default"

        self.cleanDataBase()   # clean database
        # The faker.Faker() creates and initializes a faker generator,
        self.faker = Faker()
        self.user()  # create users
        self.questionnaire()  # create questionaries
        self.question()  # create questions
        self.answer()  # create answers
        self.game()  # create games

    def cleanDataBase(self):
        # Author: Álvaro Zamanillo Sáez
        # delete all models stored (clean table)
        # in database
        # order in which data is deleted is important
        # your code goes here...
        print("clean Database")
        Guess.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Participant.objects.all().delete()
        Game.objects.all().delete()
        Questionnaire.objects.all().delete()
        User.objects.all().delete()

    def user(self):
        # Author: Pablo Cuesta Sierra
        " Insert users"
        # create user
        print("Users")

        for _ in range(self.NUMBERUSERS):
            username = self.faker.user_name()
            password = self.faker.password()
            # we log the users and passwords created
            # so that they can be later used
            # (they are encrypted in the database)
            print((
                '[populate.py]: Creating user with'
                f' username="{username}"'
                f' and password="{password}"'))
            User.objects.create_user(
                username=username,
                email=self.faker.email(),
                password=password
            )

    def questionnaire(self):
        "insert questionnaires"
        # Author: Álvaro Zamanillo Sáez
        print("questionnaire")

        for _ in range(self.NUMBERQESTIONARIES):
            q = Questionnaire()
            q.title = self.faker.word()
            q.created_at = self.faker.date_time_this_decade(
                tzinfo=timezone.get_current_timezone())
            q.updated_at = self.faker.date_time_this_decade(
                tzinfo=timezone.get_current_timezone())
            q.user = User.objects.order_by('?').first()
            q.save()

    def question(self):
        " insert questions, assign randomly to questionnaires"
        # Author: Álvaro Zamanillo Sáez
        print("Question")

        for _ in range(self.NUMBERQUESTIONS):
            q = Question()
            q.question = self.faker.sentence()
            q.created_at = self.faker.date_time_this_decade(
                tzinfo=timezone.get_current_timezone())
            q.updated_at = self.faker.date_time_this_decade(
                tzinfo=timezone.get_current_timezone())
            q.answerTime = self.faker.random_int(min=1, max=10)
            q.questionnaire = Questionnaire.objects.order_by('?').first()
            q.save()

    def answer(self):
        "insert answers, one of them must be the correct one"
        # Author: Álvaro Zamanillo Sáez
        print("Answer")
        # your code goes here
        # assign answer randomly to the questions
        # maximum number of answers per question is four
        # one of them must be the correct one

        for q in Question.objects.all():
            for _ in range(self.NUMBERANSWERPERQUESTION):
                a = Answer()
                a.answer = self.faker.sentence()
                a.correct = False
                a.question = q
                a.save()

            a = Answer.objects.filter(question=q).order_by('?').first()
            a.correct = True
            a.save()

    def game(self):
        "insert some games"
        # Author: Álvaro Zamanillo Sáez
        print("Game")
        # your code goes here
        # choose at random the questionnaries

        for _ in range(self.NUMBERGAMES):
            g = Game()
            g.created_at = self.faker.date_time_this_decade(
                tzinfo=timezone.get_current_timezone())
            g.questionnaire = Questionnaire.objects.order_by('?').first()
            g.countdownTime = self.faker.random_int(min=1, max=10)
            g.save()
