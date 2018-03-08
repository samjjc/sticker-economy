from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Sticker, TradeRequest

class StickerForm(forms.ModelForm):

    class Meta:
        model = Sticker
        fields = ('title', 'description', 'image', 'quantity')

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', )

class LogInForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ('username', 'password')

class TradeRequestForm(forms.ModelForm):

    requested_quantity = forms.IntegerField(min_value=0)
    given_quantity = forms.IntegerField(min_value=0)

    class Meta:
        model = TradeRequest
        fields = ('requested_quantity', 'given_sticker', 'given_quantity', 'message')
        
    # def __init__(self, *args, **kwargs):
        # user = kwargs.pop('user')
        # super(TradeRequestForm, self).__init__(args, kwargs)
        # print(type(user.sticker_set.all()))
        # print("TEST")
        # print(self.fields['given_sticker'])
        # self.fields['given_sticker'].choices = user.sticker_set.all()

