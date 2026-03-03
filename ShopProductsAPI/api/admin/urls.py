from django.urls import path

from user.views import (
    AdminUserListView,
    AdminUserDetailView,
    AdminChangePasswordView,
    AdminUserDeleteView,
)

urlpatterns = [
    # Admin user endpoints
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<uuid:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('users/change-password/', AdminChangePasswordView.as_view(), name='admin-change-password'),
    path('users/delete/', AdminUserDeleteView.as_view(), name='admin-user-delete'),
]
