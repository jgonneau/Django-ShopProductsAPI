from django.urls import path

from api.user.views import (
    AdminUserListView,
    AdminUserDetailView,
    AdminChangePasswordView,
    AdminUserDeleteView,
)

urlpatterns = [
    # Admin user endpoints
    path('user/', AdminUserListView.as_view(), name='admin-user-list'),
    path('user/<uuid:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('user/change-password/', AdminChangePasswordView.as_view(), name='admin-change-password'),
    path('user/delete/', AdminUserDeleteView.as_view(), name='admin-user-delete'),
]
