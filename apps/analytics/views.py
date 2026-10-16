from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.users.permissions import IsManager, IsAdminUserRole
from apps.analytics.services import AnalyticsService


class ManagerMetricsResponseSerializer(serializers.Serializer):
    total_tickets = serializers.IntegerField()
    sla_breached_count = serializers.IntegerField()
    tickets_by_priority = serializers.DictField(child=serializers.IntegerField())
    tickets_by_status = serializers.DictField(child=serializers.IntegerField())
    avg_first_response_minutes = serializers.FloatField(allow_null=True)
    agent_workload = serializers.ListField(child=serializers.DictField())


class ManagerMetricsView(APIView):
    """
    Manager dashboard metrics endpoint.
    Restricted strictly to Managers and Admins.
    """
    permission_classes = [IsAuthenticated, (IsManager | IsAdminUserRole)]

    @extend_schema(
        responses={200: ManagerMetricsResponseSerializer},
        summary="Manager Operational Metrics",
        description="Aggregated ticket counts, SLA breach metrics, and agent workload distributions.",
    )
    def get(self, request, *args, **kwargs):
        metrics = AnalyticsService.get_manager_metrics()
        return Response(metrics)