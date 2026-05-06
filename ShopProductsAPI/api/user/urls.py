from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from .auth_views import CookieTokenObtainPairView, CookieTokenRefreshView, LogoutView
from .views import (
    UserRegisterView,
    UserMeView,
    UserChangePasswordView,
    UserDeleteView,
)

urlpatterns = [
    # JWT Authentication endpoints
    path('login/', CookieTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('logout/', LogoutView.as_view(), name='token-logout'),

    # User endpoints
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('', UserMeView.as_view(), name='user-detail'),
    path('change-password/', UserChangePasswordView.as_view(), name='user-change-password'),
    path('delete/', UserDeleteView.as_view(), name='user-delete'),
]
