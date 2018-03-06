from django import forms

from .models import Sticker

class StickerForm(forms.ModelForm):

    class Meta:
        model = Sticker
        fields = ('title', 'description', 'image')