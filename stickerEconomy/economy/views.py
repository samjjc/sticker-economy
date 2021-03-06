from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Sticker, TradeRequest, Room
from django.contrib.auth.models import User
from .forms import StickerForm, SignUpForm, LogInForm, TradeRequestForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def sticker_list(request):
    sticker_list = Sticker.objects.all()
    paginator = Paginator(sticker_list, 3)
    page = request.GET.get('page', 1)
    try:
        stickers = paginator.page(page)
    except PageNotAnInteger:
        stickers = paginator.page(1)
    except EmptyPage:
        stickers = paginator.page(paginator.num_pages)
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

def sticker_delete(request, pk):
    sticker = get_object_or_404(Sticker, pk=pk)
    sticker.delete()
    return redirect('sticker_list')    

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('sticker_list')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LogInForm(data = request.POST)
        if form.is_valid():
            user = form.cleaned_data
            user = authenticate(username=user.get('username'), password=user.get('password'))
            if user is not None:
                login(request, user)
                return redirect('sticker_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('sticker_list')

def profile_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    stickers = Sticker.objects.filter(owner=user)
    requests = user.traderequest_set.filter(accepted=False)
    return render(request, 'economy/profile.html', {'stickers': stickers, 'user': user, 'requests': requests})

def sticker_trade(request, pk):
    sticker = get_object_or_404(Sticker, pk=pk)
    if request.method == 'POST':
        form = TradeRequestForm(data = request.POST, user=request.user, sticker=sticker)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.requested_sticker = sticker
            if trade.is_valid():
                trade.save()
                trade.users.add(request.user,sticker.owner)
                print(request.user.traderequest_set.values('users'))
                return redirect('sticker_list')
            else:
                messages.add_message(request, messages.WARNING, 'Invalid Request.')
    else:
        form = TradeRequestForm(user=request.user, sticker=sticker)
    return render(request, 'economy/sticker_trade.html', {'sticker': sticker, 'form': form})

def accept_trade(request, pk):
    trade = get_object_or_404(TradeRequest, pk=pk)
    trade.accepted = True
    trade.save()

    room = Room.objects.filter(users__pk=trade.given_sticker.owner.pk).filter(users__pk=trade.requested_sticker.owner.pk)
    if room.exists():
        room = room.get()
        room.active = True
        room.save()
    else:
        room = Room.objects.create(active=True)
        room.save()
        room.users.add(trade.given_sticker.owner)
        room.users.add(trade.requested_sticker.owner)
    return redirect('message')

def trade_requests(request, pk):
    sticker = get_object_or_404(Sticker, pk=pk)
    requests = sticker.requested.filter(accepted=False)
    return render(request, 'economy/trade_requests.html', {'requests': requests})

def message(request):
    current_user = request.user
    rooms = current_user.room_set.filter(active=True)
    for room in rooms:
        room.sender=room.users.exclude(pk=request.user.pk).values('username').get()['username']
    return render(request, 'economy/messages.html', {'rooms': rooms})