from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.auths.views import UserViewSet, CustomTokenRefreshView


router = DefaultRouter(trailing_slash=False)
router.register(
    prefix="users",
    viewset=UserViewSet,
    basename="user"
)

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/token/refresh", CustomTokenRefreshView.as_view(), name="token-refresh")
]
