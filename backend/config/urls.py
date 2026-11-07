from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView


urlpatterns = [
    path("admin/", admin.site.urls),

    # API REST MIL-AL
    path(
        "api/v1/",
        include("apps.users.urls"),
    ),
    path(
        "api/v1/",
        include("apps.students.urls"),
    ),
    path(
        "api/v1/",
        include("apps.academic.urls"),
    ),
    path(
        "api/v1/",
        include("apps.psychology.urls"),
    ),
    path(
        "api/v1/",
        include("apps.therapy.urls"),
    ),
    path(
        "api/v1/",
        include("apps.evaluations.urls"),
    ),
    path(
        "api/v1/",
        include("apps.reports.urls"),
    ),
    path(
        "api/v1/",
        include("apps.ai_support.urls"),
    ),
        path(
        "api/v1/",
        include("apps.dashboards.urls"),
    ),
        path(
        "api/v1/",
        include("apps.alerts.urls"),
    ),
        re_path(
        r"^(?!api/|admin/|static/).*$",
        TemplateView.as_view(template_name="index.html"),
        name="spa",
    ),
]
