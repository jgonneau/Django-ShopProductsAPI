from django.urls import path

from .views import (
    UserRegisterView,
    UserMeView,
    UserChangePasswordView,
    UserDeleteView,
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('/', UserMeView.as_view(), name='user-detail'),
    path('/change-password/', UserChangePasswordView.as_view(), name='user-change-password'),
    path('/delete/', UserDeleteView.as_view(), name='user-delete'),
]
