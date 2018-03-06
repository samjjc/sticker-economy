from django.urls import path
from . import views

urlpatterns = [
    path(r'signup/', views.signup, name='signup'),
    path('', views.sticker_list, name='sticker_list'),
    path(r'sticker/<int:pk>/', views.sticker_detail, name='sticker_detail'),
    path(r'sticker/new/', views.sticker_new, name='sticker_new'),
    path(r'post/<int:pk>/edit/', views.sticker_edit, name='sticker_edit'),
]