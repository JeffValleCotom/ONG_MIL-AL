from rest_framework import (
    exceptions,
    permissions,
    status,
    viewsets,
)
from rest_framework.response import Response

from apps.users.permissions import HasPlatformPermission

from .access import (
    get_accessible_report_queryset,
    get_report_student,
    require_report_context,
    require_report_type,
)
from .models import StudentReport
from .serializers import (
    StudentReportCreateSerializer,
    StudentReportFilterSerializer,
    StudentReportListSerializer,
    StudentReportSerializer,
)
from .services import build_report_snapshot
from django.http import HttpResponse
from rest_framework.decorators import action
from .pdf import build_report_pdf


class StudentReportViewSet(
    viewsets.GenericViewSet
):
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
        "list": "view_reports",
        "retrieve": "view_reports",
        "create": "view_reports",
        "export": "view_reports",
    }

    def get_required_permission(self):
        return self.required_permission_map.get(
            self.action
        )

    def get_context_value(self):
        context = self.request.query_params.get(
            "context",
            "",
        ).strip()

        require_report_context(
            self.request.user,
            context,
        )

        return context

    def get_queryset(self):
        context = self.get_context_value()

        queryset = get_accessible_report_queryset(
            self.request.user,
            context,
        )

        filter_serializer = (
            StudentReportFilterSerializer(
                data=self.request.query_params,
            )
        )

        filter_serializer.is_valid(
            raise_exception=True,
        )

        filters = filter_serializer.validated_data

        student_id = filters.get("student")
        report_type = filters.get("report_type")
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")

        if student_id:
            queryset = queryset.filter(
                student_id=student_id,
            )

        if report_type:
            require_report_type(
                self.request.user,
                context,
                report_type,
            )

            queryset = queryset.filter(
                report_type=report_type,
            )

        if date_from:
            queryset = queryset.filter(
                generated_at__date__gte=date_from,
            )

        if date_to:
            queryset = queryset.filter(
                generated_at__date__lte=date_to,
            )

        return queryset

    def list(self, request):
        queryset = self.get_queryset()

        serializer = StudentReportListSerializer(
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
        report = self.get_object()

        return Response(
            StudentReportSerializer(
                report
            ).data
        )

    def create(self, request):
        context = self.get_context_value()

        input_serializer = (
            StudentReportCreateSerializer(
                data=request.data,
            )
        )

        input_serializer.is_valid(
            raise_exception=True,
        )

        data = input_serializer.validated_data

        report_type = data["report_type"]

        require_report_type(
            request.user,
            context,
            report_type,
        )

        student = get_report_student(
            request.user,
            context,
            data["student_id"],
        )

        if student is None:
            raise exceptions.NotFound(
                "No Student matches the given query."
            )

        snapshot = build_report_snapshot(
            student=student,
            report_type=report_type,
            generated_by=request.user,
            generated_role=context,
            date_from=data.get("date_from"),
            date_to=data.get("date_to"),
        )

        report = StudentReport.objects.create(
            student=student,
            report_type=report_type,
            date_from=data.get("date_from"),
            date_to=data.get("date_to"),
            generated_role=context,
            content_snapshot=snapshot,
            generated_by=request.user,
        )

        return Response(
            StudentReportListSerializer(
                report
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="export",
    )
    def export(
        self,
        request,
        pk=None,
    ):
        report = self.get_object()

        pdf_content = build_report_pdf(
            report
        )

        filename = (
            "reporte-"
            f"{report.report_type.lower()}-"
            f"{report.student.institutional_code}-"
            f"{report.id}.pdf"
        )

        response = HttpResponse(
            pdf_content,
            content_type="application/pdf",
        )

        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )

        return response