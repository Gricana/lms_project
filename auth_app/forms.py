from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'birthday', 'description', 'avatar', )


class LoginForm(AuthenticationForm):
    is_remember = forms.BooleanField(label='Запомнить', label_suffix='?', required=False)

    class Meta:
        model = User
        fields = ('email', 'password', )
