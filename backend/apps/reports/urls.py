from rest_framework.routers import DefaultRouter

from .views import StudentReportViewSet


router = DefaultRouter()

router.register(
    "reports",
    StudentReportViewSet,
    basename="report",
)


urlpatterns = router.urls
