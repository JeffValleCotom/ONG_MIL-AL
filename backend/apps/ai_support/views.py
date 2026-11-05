from django.utils import timezone
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import (
    APIException,
    ValidationError,
)
from rest_framework.response import Response

from apps.users.permissions import (
    HasPlatformPermission,
)

from .access import (
    get_accessible_ai_insight_queryset,
    require_ai_context,
)
from .models import AIInsight
from .providers import AIProviderError
from .serializers import (
    AIInsightCreateSerializer,
    AIInsightDetailSerializer,
    AIInsightFilterSerializer,
    AIInsightListSerializer,
    AIInsightReviewSerializer,
)
from .services import generate_ai_insight


class AIProviderUnavailable(APIException):
    status_code = (
        status.HTTP_503_SERVICE_UNAVAILABLE
    )
    default_detail = (
        "El servicio de inteligencia "
        "artificial no está disponible."
    )
    default_code = "ai_provider_unavailable"


class AIInsightViewSet(
    viewsets.GenericViewSet
):
    permission_classes = [
        HasPlatformPermission,
    ]

    required_permission_map = {
        "list": "use_ai_assistant",
        "retrieve": "use_ai_assistant",
        "create": "use_ai_assistant",
        "review": "use_ai_assistant",
    }

    def get_required_permission(self):
        return self.required_permission_map.get(
            self.action
        )

    def get_context_value(self):
        context = (
            self.request
            .query_params
            .get("context")
        )

        return require_ai_context(
            self.request.user,
            context,
        )

    def get_queryset(self):
        context = self.get_context_value()

        queryset = (
            get_accessible_ai_insight_queryset(
                self.request.user,
                context,
            )
        )

        serializer = AIInsightFilterSerializer(
            data=self.request.query_params,
        )
        serializer.is_valid(
            raise_exception=True
        )

        filters = serializer.validated_data

        if filters.get("student"):
            queryset = queryset.filter(
                student_id=filters["student"]
            )

        if filters.get("source_report"):
            queryset = queryset.filter(
                source_report_id=(
                    filters["source_report"]
                )
            )

        if filters.get("kind"):
            queryset = queryset.filter(
                kind=filters["kind"]
            )

        if filters.get("review_status"):
            queryset = queryset.filter(
                review_status=(
                    filters["review_status"]
                )
            )

        if filters.get("date_from"):
            queryset = queryset.filter(
                created_at__date__gte=(
                    filters["date_from"]
                )
            )

        if filters.get("date_to"):
            queryset = queryset.filter(
                created_at__date__lte=(
                    filters["date_to"]
                )
            )

        return queryset

    def list(self, request):
        queryset = self.get_queryset()

        serializer = AIInsightListSerializer(
            queryset,
            many=True,
        )

        return Response(
            {
                "items": serializer.data,
            }
        )

    def retrieve(
        self,
        request,
        pk=None,
    ):
        insight = self.get_object()

        serializer = (
            AIInsightDetailSerializer(
                insight
            )
        )

        return Response(
            serializer.data
        )

    def create(self, request):
        context = self.get_context_value()

        serializer = AIInsightCreateSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        try:
            insight = generate_ai_insight(
                user=request.user,
                context=context,
                student_id=data.get(
                    "student_id"
                ),
                kind=data["kind"],
                date_from=data.get(
                    "date_from"
                ),
                date_to=data.get(
                    "date_to"
                ),
                source_report_id=data.get(
                    "source_report_id"
                ),
            )
        except AIProviderError as exc:
            raise AIProviderUnavailable() from exc
        except ValueError as exc:
            raise ValidationError(
                str(exc)
            ) from exc

        return Response(
            AIInsightDetailSerializer(
                insight
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="review",
    )
    def review(
        self,
        request,
        pk=None,
    ):
        insight = self.get_object()

        if (
            insight.kind
            == AIInsight.Kind.ANALYSIS
        ):
            raise ValidationError(
                {
                    "decision": (
                        "Los análisis informativos "
                        "no requieren aceptación "
                        "o descarte."
                    )
                }
            )

        serializer = AIInsightReviewSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        insight.review_status = (
            data["decision"]
        )
        insight.professional_notes = (
            data.get(
                "professional_notes",
                "",
            )
        )

        if "edited_content" in data:
            insight.edited_content = (
                data["edited_content"]
            )

        insight.reviewed_by = request.user
        insight.reviewed_at = timezone.now()

        insight.save(
            update_fields=[
                "review_status",
                "professional_notes",
                "edited_content",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )

        return Response(
            AIInsightDetailSerializer(
                insight
            ).data
        )
