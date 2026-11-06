from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import HasPlatformPermission

from .serializers import DashboardQuerySerializer
from .services import (
    build_dashboard_overview,
    resolve_dashboard_context,
)


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        HasPlatformPermission,
    ]

    required_permission_map = {
        "overview": "view_dashboard",
    }

    def get_required_permission(self):
        return self.required_permission_map.get(
            self.action
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="overview",
    )
    def overview(self, request):
        query_serializer = DashboardQuerySerializer(
            data=request.query_params,
        )

        query_serializer.is_valid(
            raise_exception=True
        )

        query = query_serializer.validated_data

        context = resolve_dashboard_context(
            request.user,
            query.get("context", ""),
        )

        data = build_dashboard_overview(
            request.user,
            context,
            date_from=query.get("date_from"),
            date_to=query.get("date_to"),
        )

        return Response(data)
