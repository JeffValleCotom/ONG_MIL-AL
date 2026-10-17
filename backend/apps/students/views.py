from rest_framework import mixins, permissions, viewsets

from apps.users.permissions import HasPlatformPermission

from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.all().order_by("id")
    serializer_class = StudentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        HasPlatformPermission,
    ]

    http_method_names = [
        "post",
        "head",
        "options",
    ]

    required_permission_map = {
        "create": "manage_students",
    }

    def get_required_permission(self):
        return self.required_permission_map.get(
            self.action
        )
