from django.utils import timezone
from rest_framework import (
    exceptions,
    mixins,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import HasPlatformPermission

from .models import Alert, AlertEvent
from .serializers import (
    AlertQuerySerializer,
    AlertSerializer,
)
from .services import (
    get_alert_queryset,
    resolve_alert_context,
    sync_operational_alerts,
)


class AlertViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AlertSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        HasPlatformPermission,
    ]

    required_permission_map = {
        "list": "view_alerts",
        "retrieve": "view_alerts",
        "summary": "view_alerts",
        "review": "view_alerts",
    }

    def get_required_permission(self):
        return self.required_permission_map.get(
            self.action
        )

    def get_alert_context(self):
        return resolve_alert_context(
            self.request.user,
            self.request.query_params.get(
                "context",
                "",
            ),
        )

    def get_queryset(self):
        context = self.get_alert_context()

        return get_alert_queryset(
            self.request.user,
            context,
        )

    def list(self, request, *args, **kwargs):
        query_serializer = AlertQuerySerializer(
            data=request.query_params,
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        query = query_serializer.validated_data

        context = resolve_alert_context(
            request.user,
            query.get("context", ""),
        )

        sync_operational_alerts(
            request.user,
            context,
        )

        queryset = get_alert_queryset(
            request.user,
            context,
        )

        alert_status = query.get("status")

        if alert_status:
            queryset = queryset.filter(
                status=alert_status,
            )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="summary",
    )
    def summary(self, request):
        query_serializer = AlertQuerySerializer(
            data=request.query_params,
        )
        query_serializer.is_valid(
            raise_exception=True
        )

        query = query_serializer.validated_data

        context = resolve_alert_context(
            request.user,
            query.get("context", ""),
        )

        sync_operational_alerts(
            request.user,
            context,
        )

        queryset = get_alert_queryset(
            request.user,
            context,
        )

        return Response({
            "open": queryset.filter(
                status=Alert.Status.OPEN,
            ).count(),
            "reviewed": queryset.filter(
                status=Alert.Status.REVIEWED,
            ).count(),
            "resolved": queryset.filter(
                status=Alert.Status.RESOLVED,
            ).count(),
            "total": queryset.count(),
        })

    @action(
        detail=True,
        methods=["patch"],
        url_path="review",
    )
    def review(self, request, pk=None):
        alert = self.get_object()

        if alert.status == Alert.Status.RESOLVED:
            raise exceptions.ValidationError({
                "detail": (
                    "La alerta ya se encuentra "
                    "resuelta."
                )
            })

        if alert.status == Alert.Status.REVIEWED:
            serializer = self.get_serializer(
                alert
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        previous_status = alert.status

        alert.status = Alert.Status.REVIEWED
        alert.reviewed_by = request.user
        alert.reviewed_at = timezone.now()

        alert.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )

        AlertEvent.objects.create(
            alert=alert,
            event_type=(
                AlertEvent.EventType.REVIEWED
            ),
            from_status=previous_status,
            to_status=Alert.Status.REVIEWED,
            performed_by=request.user,
            note=(
                "La alerta fue revisada por "
                "el usuario responsable."
            ),
        )

        serializer = self.get_serializer(
            alert
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
