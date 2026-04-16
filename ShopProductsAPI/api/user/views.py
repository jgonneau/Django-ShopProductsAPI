from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from api.log.models import Log, Severity

from .models import User
from .serializers import (
    UserSerializer,
    AdminUserSerializer,
    UserCreateSerializer,
    AdminUserCreateSerializer,
    UserUpdateSerializer,
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    AdminChangePasswordSerializer,
    UserDeleteSerializer,
    AdminUserDeleteSerializer,
)

# User views
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserMeView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserDeleteSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Admin views

class AdminUserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminUserCreateSerializer
        return AdminUserSerializer


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdminUserUpdateSerializer
        return AdminUserSerializer


class AdminChangePasswordView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )


class AdminUserDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminUserDeleteSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        deleted_user_id = str(serializer.user_to_delete.id)
        serializer.save()
        Log.objects.create(
            content={
                'event': 'user_deleted_by_admin',
                'user_id': deleted_user_id,
                'admin_id': str(request.user.id),
            },
            severity=Severity.INFO,
            source='api.admin'
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
