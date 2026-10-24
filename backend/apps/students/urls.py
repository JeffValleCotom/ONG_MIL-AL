from rest_framework.routers import DefaultRouter

from .views import (
    StudentProfessionalAssignmentViewSet,
    StudentViewSet,
)


router = DefaultRouter()

router.register(
    "students",
    StudentViewSet,
    basename="student",
)

router.register(
    "student-assignments",
    StudentProfessionalAssignmentViewSet,
    basename="student-assignment",
)


urlpatterns = router.urls