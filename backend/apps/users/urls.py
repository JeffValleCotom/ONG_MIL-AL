from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .auth_views import (
    CsrfTokenView,
    LoginView,
    LogoutView,
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
    "auth/logout/",
    LogoutView.as_view(),
    name="auth-logout",
    ),
]

urlpatterns += router.urls