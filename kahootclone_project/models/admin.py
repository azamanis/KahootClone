from django.contrib import admin


from .models import (
    User, Questionnaire, Question, Answer, Game, Participant, Guess
)

admin.site.register(User)
admin.site.register(Questionnaire)
admin.site.register(Question)
admin.site.register(Participant)
admin.site.register(Answer)
admin.site.register(Game)
admin.site.register(Guess)


# class QuestionnaireDetailsAdmin(admin.ModelAdmin):
#     def get_changeform_initial_data(self, request):
#         get_data = super(QuestionnaireDetailsAdmin, self
#             ).get_changeform_initial_data(request)
#         get_data['user'] = request.user.pk
#         return get_data

# admin.site.register(Questionnaire, QuestionnaireDetailsAdmin)
