from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # OpenAPI Schema & Interactive Documentation
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Core Domain Apps
    path("api/v1/", include("apps.common.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/tickets/", include("apps.tickets.urls")),
    path("api/v1/kb/", include("apps.knowledge_base.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
]