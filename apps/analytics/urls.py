from django.urls import path
from apps.analytics.views import ManagerMetricsView

urlpatterns = [
    path("manager-metrics/", ManagerMetricsView.as_view(), name="manager-metrics"),
]