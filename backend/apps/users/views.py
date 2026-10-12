from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import UserRoleAssignmentSerializer, UserSerializer


User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]

    @action(
        detail=True,
        methods=["patch"],
        url_path="activate",
    )
    def activate(self, request, pk=None):
        user = self.get_object()

        if user.is_active:
            return Response(
                {
                    "detail": "El usuario ya se encuentra activo.",
                    "user": self.get_serializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(
            {
                "detail": "Usuario activado correctamente.",
                "user": self.get_serializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="deactivate",
    )
    def deactivate(self, request, pk=None):
        user = self.get_object()

        if not user.is_active:
            return Response(
                {
                    "detail": "El usuario ya se encuentra inactivo.",
                    "user": self.get_serializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        user.is_active = False
        user.save(update_fields=["is_active"])

        return Response(
            {
                "detail": "Usuario desactivado correctamente.",
                "user": self.get_serializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get", "patch"],
        url_path="roles",
    )
    def roles(self, request, pk=None):
        user = self.get_object()

        if request.method == "GET":
            return Response(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "roles": list(
                        user.groups.order_by("name")
                        .values_list("name", flat=True)
                    ),
                },
                status=status.HTTP_200_OK,
            )

        serializer = UserRoleAssignmentSerializer(
            user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.refresh_from_db()

        return Response(
            {
                "detail": "Roles actualizados correctamente.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )