from django.shortcuts import render

# Create your views here.
def sticker_list(request):
    return render(request, 'sticker_list.html', {})