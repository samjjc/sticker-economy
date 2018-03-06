from django.shortcuts import render, get_object_or_404, redirect
from .models import Sticker
from .forms import StickerForm

# Create your views here.
def sticker_list(request):
    stickers = Sticker.objects.all()
    return render(request, 'economy/sticker_list.html', {'stickers': stickers})

def sticker_detail(request, pk):
    sticker = get_object_or_404(Sticker, pk=pk)
    return render(request, 'economy/sticker_detail.html', {'sticker': sticker})

def sticker_new(request):
    if request.method == "POST":
        form = StickerForm(request.POST, request.FILES)
        if form.is_valid():
            sticker = form.save(commit=False)
            sticker.owner = request.user
            sticker.save()
            return redirect('sticker_detail', pk=sticker.pk)
    else:
        form = StickerForm()
    return render(request, 'economy/sticker_edit.html', {'form': form})

def sticker_edit(request, pk):
    sticker = get_object_or_404(Sticker, pk=pk)
    if request.method == "POST":
        form = StickerForm(request.POST, instance=sticker)
        if form.is_valid():
            sticker = form.save(commit=False)
            sticker.owner = request.user
            sticker.save()
            return redirect('sticker_detail', pk=sticker.pk)
    else:
        form = StickerForm(instance=sticker)
    return render(request, 'economy/sticker_edit.html', {'form': form})