from django.contrib import admin

from .models import Alert, AlertEvent


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "condition",
        "assigned_to",
        "assigned_role",
        "status",
        "detected_at",
    )

    list_filter = (
        "condition",
        "status",
        "assigned_role",
    )

    search_fields = (
        "student__institutional_code",
        "student__first_name",
        "student__last_name",
        "assigned_to__username",
    )


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "alert",
        "event_type",
        "from_status",
        "to_status",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "event_type",
        "to_status",
    )
