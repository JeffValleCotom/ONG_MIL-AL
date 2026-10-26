from rest_framework.routers import DefaultRouter

from .views import AcademicFollowUpViewSet


router = DefaultRouter()

router.register(
    "academic-followups",
    AcademicFollowUpViewSet,
    basename="academic-followup",
)


urlpatterns = router.urls
