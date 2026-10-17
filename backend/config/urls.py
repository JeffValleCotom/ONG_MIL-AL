from django.contrib import admin
from django.urls import include, path


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
]
