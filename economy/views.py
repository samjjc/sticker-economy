from django.shortcuts import render
from .models import Sticker

# Create your views here.
def sticker_list(request):
    stickers = Sticker.objects.all()
    return render(request, 'sticker_list.html', {'stickers': stickers})