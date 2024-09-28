from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpForm(UserCreationForm):
    ''' Form to register a new user'''
    # Author: Pablo Cuesta Sierra
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', )
