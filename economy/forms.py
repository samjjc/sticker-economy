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

    given_quantity = forms.IntegerField(min_value=0, initial=1)

    class Meta:
        model = TradeRequest
        fields = ('requested_quantity', 'given_sticker', 'given_quantity', 'message')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        sticker = kwargs.pop('sticker')
        super(TradeRequestForm, self).__init__(*args, **kwargs)
        self.fields['given_sticker'].queryset = user.sticker_set.all()
        self.fields['requested_quantity']= forms.IntegerField(min_value=0,initial=1, max_value=sticker.quantity)
    

