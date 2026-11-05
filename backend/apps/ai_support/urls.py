from rest_framework.routers import (
    DefaultRouter,
)

from .views import AIInsightViewSet


router = DefaultRouter()

router.register(
    "ai-insights",
    AIInsightViewSet,
    basename="ai-insight",
)


urlpatterns = router.urls
