from django.db.models import Q
from rest_framework import (
    mixins,
    permissions,
    serializers,
    viewsets,
)

from apps.users.permissions import HasPlatformPermission

from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        HasPlatformPermission,
    ]

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
    ]

    required_permission_map = {
        "list": "view_students",
        "retrieve": "view_students",
        "create": "manage_students",
    }

    def get_required_permission(self):
        return self.required_permission_map.get(
            self.action
        )

    def get_queryset(self):
        queryset = Student.objects.all().order_by(
            "last_name",
            "first_name",
            "institutional_code",
        )

        if self.action != "list":
            return queryset

        search = (
            self.request.query_params
            .get("search", "")
            .strip()
        )

        if search:
            queryset = queryset.filter(
                Q(institutional_code__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        status_filter = (
            self.request.query_params
            .get("status", "")
            .strip()
            .lower()
        )

        if status_filter:
            status_values = {
                "active": True,
                "inactive": False,
            }

            if status_filter not in status_values:
                raise serializers.ValidationError(
                    {
                        "status": (
                            "El estado debe ser "
                            "'active' o 'inactive'."
                        )
                    }
                )

            queryset = queryset.filter(
                is_active=status_values[
                    status_filter
                ]
            )

        return queryset
