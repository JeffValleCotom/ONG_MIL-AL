from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .profile_views import ProfileView
from .auth_views import (
    CsrfTokenView,
    LoginView,
    LogoutView,
    PasswordChangeView,
    SessionView,
)

router = DefaultRouter()

router.register(
    "users",
    UserViewSet,
    basename="user",
)


urlpatterns = [
    path(
        "auth/csrf/",
        CsrfTokenView.as_view(),
        name="auth-csrf",
    ),
    path(
        "auth/login/",
        LoginView.as_view(),
        name="auth-login",
    ),
    path(
        "auth/session/",
        SessionView.as_view(),
        name="auth-session",
    ),

    path(
        "auth/password/change/",
        PasswordChangeView.as_view(),
        name="auth-password-change",
    ),

    path(
        "auth/logout/",
        LogoutView.as_view(),
        name="auth-logout",
    ),

    path(
        "profile/",
        ProfileView.as_view(),
        name="user-profile",
    ),
]

urlpatterns += router.urls