from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import connection
from django.core.cache import cache
from drf_spectacular.utils import extend_schema


class HealthCheckResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    database = serializers.CharField()
    cache = serializers.CharField()


class HealthCheckView(APIView):
    """
    Basic health check endpoint reporting DB, cache, and service status.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: HealthCheckResponseSerializer, 503: HealthCheckResponseSerializer},
        summary="Service Health Check",
        description="Checks database and Redis cache connectivity.",
    )
    def get(self, request, *args, **kwargs):
        health_status = {
            "status": "healthy",
            "database": "unknown",
            "cache": "unknown",
        }

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
            health_status["database"] = "reachable"
        except Exception as exc:
            health_status["database"] = f"unreachable: {str(exc)}"
            health_status["status"] = "unhealthy"

        try:
            cache.set("health_check_ping", "pong", timeout=5)
            if cache.get("health_check_ping") == "pong":
                health_status["cache"] = "reachable"
            else:
                health_status["cache"] = "unavailable"
                health_status["status"] = "unhealthy"
        except Exception as exc:
            health_status["cache"] = f"unreachable: {str(exc)}"
            health_status["status"] = "unhealthy"

        http_status = (
            status.HTTP_200_OK
            if health_status["status"] == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return Response(health_status, status=http_status)