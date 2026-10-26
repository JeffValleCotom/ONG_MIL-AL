from rest_framework.routers import DefaultRouter

from .views import PsychologicalFollowUpViewSet


router = DefaultRouter()

router.register(
    "psychological-followups",
    PsychologicalFollowUpViewSet,
    basename="psychological-followup",
)


urlpatterns = router.urls
