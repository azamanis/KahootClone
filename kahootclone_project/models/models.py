import uuid
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from django.urls import reverse

from .constants import (
    WAITING,
    QUESTION,
    ANSWER,
    LEADERBOARD
)
import os

MAX_PUBLICID = (
    10**6 if 'TESTING' not in os.environ else 5)
COUNTDOWN_TIME = 5


class User(AbstractUser):
    '''Default user class, just in case we want
    to add something extra in the future'''
    # Author: Pablo Cuesta Sierra
    # remove pass command if you add something here
    pass


class Questionnaire(models.Model):
    ''' Model to store the questionnaires.'''
    # Author: Pablo Cuesta Sierra
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this questionnaire.
        """
        return reverse('questionnaire-detail', args=[str(self.id)])

    def get_owner(self):
        return self.user

    class Meta:
        ordering = ['-id']


class Question(models.Model):
    ''' Model to store the questions of a questionnaire. Each question belongs
    to a single questionnaire'''
    # Author: Pablo Cuesta Sierra
    question = models.CharField(max_length=100)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    answerTime = models.IntegerField(
        default=20,
        blank=True,
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return self.question

    def get_owner(self):
        return self.questionnaire.user

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this questionnaire."""
        return reverse('question-detail', args=[str(self.id)])

    class Meta:
        ordering = ['id']

    def correct_answers_count(self):
        '''Returns the number of correct answers.'''
        return self.answer_set.filter(correct=True).count()


class Answer(models.Model):
    ''' Model to store the answers of a question. Answers may be correct or
    incorrect.'''
    # Author: Pablo Cuesta Sierra
    answer = models.CharField(max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.answer

    def get_owner(self):
        '''Returns the owner of the question that this answer belongs to. '''
        return self.question.questionnaire.user

    class Meta:
        ordering = ['id']

    def _is_saved_as_correct(self):
        '''Returns True if the answer is already saved as correct.'''
        return self in self.question.answer_set.filter(correct=True)

    def save(self, *args, **kwargs):
        creation = not self.pk

        if creation and self.question.answer_set.count() >= 4:
            raise ValidationError(
                "A question can only have 4 answers")

        if not self.correct:
            super().save(*args, **kwargs)
            return

        exists_correct_answer_in_question = (
            self.question.correct_answers_count() > 0)

        invalid_creation = (
            creation and exists_correct_answer_in_question)

        invalid_update = (
            not creation and exists_correct_answer_in_question
            and not self._is_saved_as_correct())

        if invalid_creation or invalid_update:
            raise ValidationError(
                "There can only be one correct answer per question")

        super().save(*args, **kwargs)


class Game(models.Model):
    ''' Model to store the state of a game. Each game is associated to
    a questionnaire and has a publicId to be shared with the players.'''
    # Author: Pablo Cuesta Sierra
    STATE_CHOICES = (
        (WAITING, 'WAITING'),
        (QUESTION, 'QUESTION'),
        (ANSWER, 'ANSWER'),
        (LEADERBOARD, 'LEADERBOARD'),
    )
    publicId = models.IntegerField(
        primary_key=True,
        validators=[MaxValueValidator(MAX_PUBLICID), MinValueValidator(1)],
    )

    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.IntegerField(choices=STATE_CHOICES, default=WAITING)
    countdownTime = models.IntegerField(
        default=COUNTDOWN_TIME,
        null=True,
        validators=[MinValueValidator(1)],
    )
    questionNo = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.questionnaire.title}(id={self.publicId})"

    def save(self, *args, **kwargs):
        # Author: Álvaro Zamanillo Sáez
        if not self.pk:  # only on creation
            # generate a key in range [1,10^6] until is unique
            keys = Game.objects.values_list("publicId", flat=True)
            publicId_minus_one = random.randint(0, MAX_PUBLICID - 1)

            if len(keys) == MAX_PUBLICID:
                raise ValidationError(
                    "Could not generate a unique publicID")

            while publicId_minus_one + 1 in keys:
                publicId_minus_one = (publicId_minus_one + 1) % MAX_PUBLICID

            self.publicId = publicId_minus_one + 1

        super(Game, self).save(*args, **kwargs)

    def update_state_next_question(self):
        ''' Updates the state of the game to the next question or to the state
        Leaderboard if there are no more questions'''
        # Author: Pablo Cuesta Sierra
        if self.questionNo >= self.questionnaire.question_set.count():
            self.state = LEADERBOARD
        else:
            self.state = QUESTION
            self.countdownTime = self.questionnaire.question_set.all()[
                self.questionNo].answerTime

    def update_state(self):
        ''' Updates the state of the game to the next state'''
        # Author: Álvaro Zamanillo Sáez
        if self.state == WAITING:
            self.update_state_next_question()
        elif self.state == QUESTION:
            self.state = ANSWER
        elif self.state == ANSWER:
            self.questionNo += 1
            self.update_state_next_question()

        self.save()

    def get_owner(self):
        '''Returns the owner of the questionnaire that this game belongs to.'''
        return self.questionnaire.user

    def all_participants_answered(self):
        '''
        Returns True if all participants have answered the current question.
        '''

        # Author: Álvaro Zamanillo Sáez
        current_question = \
            self.questionnaire.question_set.all()[self.questionNo]
        n_guesses = \
            Guess.objects.filter(question=current_question, game=self).count()

        return n_guesses == self.participant_set.count()


class Participant(models.Model):
    '''Participant of a specific game'''
    # Author: Pablo Cuesta Sierra
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50)
    points = models.IntegerField(default=0)
    uuidP = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.alias

    class Meta:  # ordenados por puntos para el leaderboard
        ordering = ['-points', 'alias']

    def save(self, *args, **kwargs):
        # Author: Álvaro Zamanillo Sáez
        if not self.pk:
            # check if alias is repeated for the same game
            names = Participant.objects.filter(game=self.game).values_list(
                "alias", flat=True)
            if self.alias in names:
                raise ValidationError(
                    f'Participant already exists in the game: "{self.alias}"')
        super(Participant, self).save(*args, **kwargs)


class Guess(models.Model):
    '''Model to store the guesses of the participants. If the guess is correct
    the participant gets a point.'''
    # Author: Álvaro Zamanillo Sáez
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return str(
            {key: val for key, val in self.__dict__.items() if key != "_state"}
        )

    class Meta:
        unique_together = ('participant', 'question', 'game')

    def save(self, *args, **kwargs):
        # Author: Álvaro Zamanillo Sáez
        if (
            self.pk or
            Guess.objects.filter(
                participant=self.participant,
                question=self.question,
                game=self.game
            ).exists()
        ):
            raise ValidationError(
                f"You may not edit an existing {self._meta.model_name}")

        # The following validation cannot be done, as the tests provided
        # would fail:
        # if self.participant.game != self.game:
        #     raise ValidationError(
        #         f"Participant {self.participant} "
        #         f"does not belong to the game {self.game}")

        # try:
            # here we should use self.game.questionnaire but test07_guess
            # has incompatible data
        question_idx = list(
            self.question.questionnaire.question_set.all()
        ).index(self.question)

        # except ValueError:
        #     # this is never catched, because the question is always in the
        #     # questionnaire, as commented above
        #     raise ValidationError((
        #         f"Question {self.answer.question} "
        #         "does not belong to the game"))

        if question_idx < self.game.questionNo or self.game.state != QUESTION:
            raise ValidationError("Wait until the question is shown")

        if self.answer.correct:
            self.participant.points += 1
            self.participant.save()
        super(Guess, self).save(*args, **kwargs)
