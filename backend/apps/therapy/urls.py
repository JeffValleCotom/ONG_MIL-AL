from rest_framework.routers import DefaultRouter

from .views import TherapyFollowUpViewSet


router = DefaultRouter()

router.register(
    "therapy-followups",
    TherapyFollowUpViewSet,
    basename="therapy-followup",
)


urlpatterns = router.urls
