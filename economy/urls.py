from django.urls import path
from . import views

urlpatterns = [
    path('', views.sticker_list, name='sticker_list'),
]