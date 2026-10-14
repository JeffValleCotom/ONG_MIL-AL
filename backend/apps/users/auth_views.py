from django.contrib.auth import login as django_login
from django.middleware.csrf import get_token
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, UserSerializer


class CsrfTokenView(APIView):
    """
    Entrega un token CSRF al cliente antes de realizar
    operaciones de autenticación mediante sesión.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "csrfToken": get_token(request),
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    """
    Valida las credenciales y crea una sesión de Django.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # DRF exime sus APIView del middleware CSRF por defecto.
        # Por eso lo exigimos explícitamente en el inicio de sesión.
        SessionAuthentication().enforce_csrf(request)

        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        django_login(request, user)

        return Response(
            {
                "detail": "Sesión iniciada correctamente.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class SessionView(APIView):
    """
    Informa al frontend si existe una sesión autenticada.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {
                    "authenticated": False,
                    "user": None,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "authenticated": True,
                "user": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )