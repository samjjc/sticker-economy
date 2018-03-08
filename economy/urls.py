from django.urls import path
from . import views

urlpatterns = [
    path('', views.sticker_list, name='sticker_list'),
    path(r'sticker/<int:pk>/', views.sticker_detail, name='sticker_detail'),
    path(r'sticker/new/', views.sticker_new, name='sticker_new'),
    path(r'post/<int:pk>/edit/', views.sticker_edit, name='sticker_edit'),
    path(r'post/<int:pk>/delete/', views.sticker_delete, name='sticker_delete'),
    path(r'signup/', views.signup_view, name='signup'),
    path(r'login/', views.login_view, name='login'),
    path(r'logout/', views.logout_view, name='logout'),
    path(r'profile/<int:pk>', views.profile_view, name='profile'),
    path(r'sticker/<int:pk>/trade/', views.sticker_trade, name='sticker_trade'),
    path(r'sticker/<int:pk>/trades/', views.trade_requests, name='trade_requests'),
    path(r'trade/<int:pk>/', views.trade, name='trade'),
]