from django.http import HttpResponse
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin)

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    TemplateView, DetailView, ListView, CreateView,
    DeleteView, UpdateView
)

# Create your views here.
from models.models import (
    Answer, Game, Question, Questionnaire, Participant, Guess
)

from models.constants import (
    WAITING, QUESTION, ANSWER, LEADERBOARD,)

state_template = {
    WAITING: 'game_countdown.html',
    QUESTION: 'game_question.html',
    ANSWER: 'game_answer.html',
    LEADERBOARD: 'game_leaderboard.html'
}
MAX_ANSWERS = 4
MAX_CORRECT_ANSWERS = 1
OWNER_ALLOWED = 3


class HomeView(TemplateView):
    # Author: Pablo Cuesta Sierra
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['latest_questionnaire_list'] = Questionnaire.objects. \
                filter(user=self.request.user).order_by('-updated_at')[:5]
        return context


class OwnerMixin(UserPassesTestMixin):
    ''''
        Checks that user logged is owner of object and
        that a user is logged.
    '''
    # Author: Álvaro Zamanillo Sáez

    _response = HttpResponseForbidden(
        "Resource does not belong to logged user")

    def test_func(self):
        # Author: Álvaro Zamanillo Sáez
        if not self.request.user.is_authenticated:
            self._response = HttpResponseRedirect(reverse('login'))
            return False

        owner = self._owner()

        return (
            ((owner == OWNER_ALLOWED) or (owner == self.request.user))
            if owner else False
        )

    def _owner(self):
        # Author: Pablo Cuesta Sierra
        if isinstance(self, ListView):
            qset = self.get_queryset()
            if qset.count() > 0:
                return qset.first().get_owner()
            else:
                # if list is empty, allow access
                return OWNER_ALLOWED
        else:
            return self.get_object().get_owner()

    def handle_no_permission(self):
        # Author: Álvaro Zamanillo Sáez
        return self._response


class QuestionnaireDetailView(OwnerMixin, DetailView):
    ''' Detail view of a questionnaire'''
    # Author: Pablo Cuesta Sierra
    model = Questionnaire


class QuestionnaireListView(OwnerMixin, ListView):
    ''' List view of questionnaires of a user'''
    # Author: Pablo Cuesta Sierra
    model = Questionnaire
    paginate_by = 10

    def get_queryset(self):
        return Questionnaire.objects.filter(user=self.request.user)


class QuestionnaireDelete(OwnerMixin, DeleteView):
    ''' Delete view of a questionnaire. After delete the user is redirected
        to the list of questionnaires.'''
    # Author: Pablo Cuesta Sierra
    model = Questionnaire
    success_url = reverse_lazy('questionnaire-list')


class QuestionnaireUpdate(OwnerMixin, UpdateView):
    ''' Update view of a questionnaire.'''
    # Author: Pablo Cuesta Sierra
    model = Questionnaire
    fields = ['title']


class QuestionnaireCreate(LoginRequiredMixin, CreateView):
    ''' Create view of a questionnaire. On success, the user is redirected
        to the detail view of the questionnaire.'''
    # Author: Pablo Cuesta Sierra
    model = Questionnaire
    fields = ['title']

    def form_valid(self, form):
        # Author: Álvaro Zamanillo Sáez
        self.object = form.save(False)

        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


# Question ######################################


class QuestionCreate(OwnerMixin, CreateView):
    ''' Create view of a question. On success, the user is redirected
        to the detail view of the questionnaire.'''
    # Author: Álvaro Zamanillo Sáez
    model = Question
    fields = ['question', 'answerTime']
    initial = {'answerTime': 20}

    def get_questionnaire(self):
        # Author: Álvaro Zamanillo Sáez
        return Questionnaire.objects.filter(
            id=self.kwargs['questionnaireid']).first()

    def _owner(self):
        # Author: Pablo Cuesta Sierra
        return self.get_questionnaire().get_owner()

    def form_valid(self, form):
        # Author: Álvaro Zamanillo Sáez
        self.object = form.save(False)
        self.object.questionnaire = self.get_questionnaire()
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class QuestionDetailView(OwnerMixin, DetailView):
    ''' Detail view of a question.'''
    # Author: Álvaro Zamanillo Sáez
    model = Question


class QuestionDelete(OwnerMixin, DeleteView):
    ''' Delete view of a question. After deleting it, the user is redirected
        to the detail view of the questionnaire.'''
    # Author: Álvaro Zamanillo Sáez
    model = Question

    def get_success_url(self):
        return reverse_lazy('questionnaire-detail',
                            kwargs={'pk': self.object.questionnaire.id})


class QuestionUpdate(OwnerMixin, UpdateView):
    ''' Update view of a question.'''
    # Author: Álvaro Zamanillo Sáez
    model = Question
    fields = ['question', 'answerTime']


# Answer ######################################

class AnswerCreate(OwnerMixin, CreateView):
    ''' Create view of an answer. On success, the user is redirected
        to the detail view of the question.'''
    # Author: Álvaro Zamanillo Sáez
    model = Answer
    fields = ['answer', 'correct']

    exists_correct_answer = None

    def get_question(self):
        # Author: Pablo Cuesta Sierra
        return Question.objects.filter(
            id=self.kwargs['questionid']).first()

    def _owner(self):
        # Author: Pablo Cuesta Sierra
        return self.get_question().get_owner()

    def _exists_correct_answer(self):
        ''' Checks if there is already a correct answer for the question.
        Only one correct answer is allowed per question.'''
        # Author: Pablo Cuesta Sierra
        if not self.exists_correct_answer:
            self.exists_correct_answer = (
                self.get_question().correct_answers_count() > 0)
        return self.exists_correct_answer

    def get_context_data(self, **kwargs):
        # Author: Álvaro Zamanillo Sáez
        context = super().get_context_data(**kwargs)
        context['disable_correct'] = self._exists_correct_answer()

        return context

    def get_form(self):
        ''' If there is already a correct answer, the correct field is not
            shown in the form.'''
        # Author: Álvaro Zamanillo Sáez
        self.fields = (
            ['answer'] + (
                ['correct'] if not self._exists_correct_answer()
                else []
            )
        )

        return super().get_form()

    def form_valid(self, form):
        question = self.get_question()

        # Extra check that there is already a correct answer before saving.
        if question.answer_set.count() >= MAX_ANSWERS:
            return HttpResponseForbidden(
                f"Maximum {MAX_ANSWERS} answers per question"
            )

        self.object = form.save(False)

        self.object.question = question
        self.object.save()

        # redirect to question detail
        return HttpResponseRedirect(self.object.question.get_absolute_url())


class AnswerDelete(OwnerMixin, DeleteView):
    ''' Delete view of an answer. After deleting it, the user is redirected
        to the detail view of the question.'''
    # Author: Álvaro Zamanillo Sáez

    model = Answer

    def get_success_url(self):
        return reverse_lazy('question-detail',
                            kwargs={'pk': self.object.question.id})


class AnswerUpdate(OwnerMixin, UpdateView):
    ''' Update view of an answer. After updating it, the user is redirected
        to the detail view of the question.'''
    # Author: Álvaro Zamanillo Sáez
    model = Answer
    fields = ['answer', 'correct']

    exists_correct_answer = None

    def get_question(self):
        # Author: Pablo Cuesta Sierra
        return self.get_object().question

    def _exists_correct_answer(self):
        ''' Checks if there is already a correct answer for the question.
        Only one correct answer is allowed per question.'''
        # Author: Pablo Cuesta Sierra
        if not self.exists_correct_answer:
            self.exists_correct_answer = (
                self.get_question().correct_answers_count() > 0)
        return self.exists_correct_answer

    def _can_change_correct(self):
        ''' Checks if the correct field can be changed. It can be changed
            if there is no correct answer or if the answer is already
            correct.'''
        # Author: Pablo Cuesta Sierra
        return (
            not self._exists_correct_answer()
            or self.get_object().correct
        )

    def get_context_data(self, **kwargs):
        # Author: Pablo Cuesta Sierra
        context = super().get_context_data(**kwargs)
        context['disable_correct'] = not self._can_change_correct()

        return context

    def get_form(self):
        ''' If there is already a correct answer, the correct field is not
            shown in the form.'''
        # Author: Pablo Cuesta Sierra
        self.fields = (
            ['answer'] + (
                ['correct'] if self._can_change_correct()
                else []
            )
        )

        return super().get_form()

    def form_valid(self, form):
        question = self.get_question()

        self.object = form.save(False)

        self.object.question = question
        self.object.save()

        # redirect to question detail
        return HttpResponseRedirect(self.object.question.get_absolute_url())


# GAME ######################################

class GameCreate(OwnerMixin, TemplateView):
    ''' Create view of a game. Once the game is created, a html with the
    publicID is shown to allow participants join the game.'''
    # Author: Álvaro Zamanillo Sáez
    template_name = 'game_start.html'
    questionnaire = None

    def get_questionnaire(self):
        # Author: Pablo Cuesta Sierra
        if not self.questionnaire:
            self.questionnaire = Questionnaire.objects.filter(
                id=self.kwargs['questionnaireid']).first()
        return self.questionnaire

    def _owner(self):
        # Author: Pablo Cuesta Sierra
        return self.get_questionnaire().get_owner()

    def get_context_data(self, **kwargs):
        # Author: Álvaro Zamanillo Sáez
        questionnaire = self.get_questionnaire()

        game = Game(questionnaire=questionnaire)
        game.save()

        self.request.session['publicId'] = game.publicId
        self.request.session['started'] = False

        context = super().get_context_data(**kwargs)
        context['publicId'] = game.publicId

        return context


class GameUpdateParticipant(OwnerMixin, ListView):
    '''View to fill the participant's name alias in an auxiliar html.
    This html (with the list of alias) will be shown before the game starts.'''
    # Author: Álvaro Zamanillo Sáez
    model = Participant
    context_object_name = 'participants'
    template_name = 'participants_container.html'

    def get_game(self):
        # Author: Álvaro Zamanillo Sáez
        return Game.objects.filter(
            publicId=self.request.session['publicId']).first()

    def _owner(self):
        # Author: Pablo Cuesta Sierra
        try:
            return self.get_game().get_owner()
        except KeyError:
            return None

    def get_queryset(self):
        '''Returns the game's list of participants.
        Optional input: alias (participant's name to be deleted from the game)
        '''
        # Author: Álvaro Zamanillo Sáez
        game = self.get_game()

        return super().get_queryset().filter(game=game)


class GameCountdown(TemplateView):
    ''' View to control the whole game. It shows the different templates
    according to the game state. Each time is executed, the game state is
    updated.'''

    # Author: Álvaro Zamanillo Sáez
    game = None

    def set_game(self):
        ''' Sets the game object in the view. It will be used
        in several methods.'''
        # Author: Álvaro Zamanillo Sáez
        self.game = Game.objects.filter(
            publicId=self.request.session['publicId']).first()

    def dispatch(self, request, *args, **kwargs):
        '''first function to execute'''
        # Author: Álvaro Zamanillo Sáez
        self.set_game()

        if self.request.session['started']:
            self.game.update_state()
        # the first time GameCountdown is called, the game state must not be
        # updated.
        else:
            self.request.session['started'] = True

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        ''' Returns the template name according to the game state. This
        function is executed after the game state has been updated. (it is
        the last function of the class executed)'''
        # Author: Álvaro Zamanillo Sáez
        return state_template[self.game.state]

    def get_context_data(self, **kwargs):
        # Author: Álvaro Zamanillo Sáez
        context = super().get_context_data(**kwargs)
        game = context['game'] = self.game
        state = game.state

        if state not in (LEADERBOARD, WAITING):
            question = game.questionnaire.question_set.all()[game.questionNo]
            context['question'] = question

            num_answers = context['question'].answer_set.count()

            context['answers'] = (
                list(context['question'].answer_set.all())
                + (MAX_ANSWERS - num_answers) * [None]
            )

        if state == ANSWER:
            correct_answer = (
                game.questionnaire.question_set
                .all()[game.questionNo].answer_set
                .filter(correct=True).first()
            )

            context['correct_answer'] = correct_answer

            all_guesses = Guess.objects.filter(game=game, question=question)
            total_guesses = context['num_total_guesses'] = all_guesses.count()
            context['num_correct_guesses'] = (
                all_guesses.filter(answer=correct_answer).count())
            context['participants'] = game.participant_set.all()

            all_answers = question.answer_set.all()
            answers_count = [
                all_guesses.filter(answer=answer).count()
                for answer in all_answers
            ]
            context['answers_proportions'] = [
                f"{answer_count/total_guesses if total_guesses else 0:.2%}"
                for answer_count in answers_count
            ]

        return context


def checkAllAnswered(request):
    ''' Checks if all participants have answered the current question in the
    currently active game.
    Returns a string witih "True" if all have answered or "False" otherwise.'''
    # Author: Álvaro Zamanillo Sáez

    game = Game.objects.filter(
        publicId=request.session['publicId']).first()

    return HttpResponse(game.all_participants_answered() if game else "False")


def deleteParticipant(request, alias):
    '''Deletes a participant from the currently active game.
    Input: alias: alias of the participant to be deleted'''
    # Author: Álvaro Zamanillo Sáez

    # get the current game
    game = Game.objects.filter(
        publicId=request.session['publicId']).first()

    # get the participant to delete
    participant = Participant.objects.filter(
        game=game, alias=alias).first()
    if participant:
        participant.delete()

    return HttpResponse("")
