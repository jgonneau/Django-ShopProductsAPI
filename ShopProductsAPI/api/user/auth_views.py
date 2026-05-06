from django.conf import settings
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def _refresh_cookie_name() -> str:
    return getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'refresh_token')


def _refresh_cookie_path() -> str:
    return getattr(settings, 'JWT_AUTH_REFRESH_COOKIE_PATH', '/api/user/token/refresh/')


def _refresh_cookie_domain() -> str | None:
    return getattr(settings, 'JWT_AUTH_REFRESH_COOKIE_DOMAIN', None)


def _refresh_cookie_samesite() -> str:
    return getattr(settings, 'JWT_AUTH_REFRESH_COOKIE_SAMESITE', 'Lax')


def _refresh_cookie_secure() -> bool:
    return getattr(settings, 'JWT_AUTH_REFRESH_COOKIE_SECURE', True)


def _refresh_cookie_max_age() -> int:
    return int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=_refresh_cookie_name(),
        value=refresh_token,
        max_age=_refresh_cookie_max_age(),
        httponly=True,
        secure=_refresh_cookie_secure(),
        samesite=_refresh_cookie_samesite(),
        path=_refresh_cookie_path(),
        domain=_refresh_cookie_domain(),
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=_refresh_cookie_name(),
        path=_refresh_cookie_path(),
        domain=_refresh_cookie_domain(),
        samesite=_refresh_cookie_samesite(),
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code != status.HTTP_200_OK:
            return response

        refresh_token = response.data.pop('refresh', None)
        if refresh_token:
            _set_refresh_cookie(response, refresh_token)

        return response


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField(required=False)

    def validate(self, attrs):
        refresh = attrs.get('refresh')
        request = self.context.get('request')

        if not refresh and request is not None:
            refresh = request.COOKIES.get(_refresh_cookie_name())

        if not refresh:
            raise InvalidToken('Refresh token not provided.')

        attrs['refresh'] = refresh
        return super().validate(attrs)


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = CookieTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code != status.HTTP_200_OK:
            return response

        rotated_refresh = response.data.pop('refresh', None)
        if rotated_refresh:
            _set_refresh_cookie(response, rotated_refresh)

        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(_refresh_cookie_name())

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except (TokenError, AttributeError):
                pass

        response = Response(status=status.HTTP_205_RESET_CONTENT)
        _clear_refresh_cookie(response)
        return response
