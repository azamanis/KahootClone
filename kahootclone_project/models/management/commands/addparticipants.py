from faker import Faker
import time
from django.core.management.base import BaseCommand

from models.models import Game, Participant


class Command(BaseCommand):
    # Author: Pablo Cuesta Sierra
    help = """Create participants for a game"""

    def add_arguments(self, parser):
        parser.add_argument(
            'sleep_seconds',
            type=float,
            default=.5,
            help='wait this seconds until inserting next participant',
        )
        parser.add_argument(
            'num_participants',
            type=int,
            default=5,
            help='total number of participants to create',
        )
        parser.add_argument(
            'publicId',
            type=int,
            help='game the participants will join to'
        )

    def handle(self, *args, **kwargs):
        """this function will be executed by default"""

        self.faker = Faker()

        # get the arguments
        self.sleep_seconds = kwargs.get('sleep_seconds')
        self.game = Game.objects.get(publicId=kwargs.get('publicId'))
        self.num_participants = kwargs.get('num_participants')

        try:
            self.create_participants()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: ending script")
        except Exception as e:
            print(e)

    def create_participants(self):
        for i in range(self.num_participants):
            Participant.objects.create(
                game=self.game,
                alias=self.faker.user_name(),
            )
            print("Participant {} created".format(i))
            time.sleep(self.sleep_seconds)
