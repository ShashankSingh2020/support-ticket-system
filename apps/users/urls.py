from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import (
    CustomTokenObtainPairView,
    RegisterCustomerView,
    CurrentUserProfileView,
    TeamViewSet,
)

router = DefaultRouter()
router.register(r"teams", TeamViewSet, basename="team")

urlpatterns = [
    path("auth/register/", RegisterCustomerView.as_view(), name="auth-register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("auth/me/", CurrentUserProfileView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]