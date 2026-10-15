from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import (
    get_user_model,
    login as django_login,
    logout as django_logout,
    update_session_auth_hash,
)
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordRecoveryRequestSerializer,
    UserSerializer,
)


User = get_user_model()


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


class PasswordChangeView(APIView):
    """
    Permite al usuario autenticado cambiar su propia contraseña.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(
            raise_exception=True
        )

        user = request.user

        user.set_password(
            serializer.validated_data[
                "new_password"
            ]
        )
        user.save(
            update_fields=["password"]
        )

        update_session_auth_hash(
            request,
            user,
        )

        return Response(
            {
                "detail": (
                    "Contraseña actualizada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordRecoveryRequestView(APIView):
    """
    Inicia el proceso público de recuperación de contraseña
    sin revelar si el correo pertenece a una cuenta registrada.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    generic_message = (
        "Si existe una cuenta asociada, se enviarán "
        "instrucciones de recuperación."
    )

    def post(self, request):
        serializer = PasswordRecoveryRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data[
            "email"
        ]

        users = User.objects.filter(
            email__iexact=email,
            is_active=True,
        )

        for user in users:
            if not user.has_usable_password():
                continue

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )
            token = default_token_generator.make_token(
                user
            )

            query_string = urlencode(
                {
                    "uid": uid,
                    "token": token,
                }
            )

            separator = (
                "&"
                if "?" in settings.PASSWORD_RESET_FRONTEND_URL
                else "?"
            )

            recovery_url = (
                f"{settings.PASSWORD_RESET_FRONTEND_URL}"
                f"{separator}{query_string}"
            )

            send_mail(
                subject=(
                    "Recuperación de contraseña - MIL-AL"
                ),
                message=(
                    "Se recibió una solicitud para restablecer "
                    "la contraseña de su cuenta MIL-AL.\n\n"
                    "Utilice el siguiente enlace para continuar:\n"
                    f"{recovery_url}\n\n"
                    "Si usted no realizó esta solicitud, "
                    "puede ignorar este mensaje."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

        return Response(
            {
                "detail": self.generic_message,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    Finaliza la sesión autenticada del usuario.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        django_logout(request)

        return Response(
            {
                "detail": "Sesión cerrada correctamente.",
            },
            status=status.HTTP_200_OK,
        )
