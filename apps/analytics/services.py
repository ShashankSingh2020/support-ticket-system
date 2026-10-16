from django.db.models import Count, Avg, F, DurationField, ExpressionWrapper, Q
from apps.tickets.models import Ticket
from apps.users.models import User


class AnalyticsService:
    @staticmethod
    def get_manager_metrics():
        """
        Database-level aggregations computing queue statistics and SLA metrics.
        Avoids loading all tickets into Python memory.
        """
        total_tickets = Ticket.objects.count()
        breached_tickets = Ticket.objects.filter(sla_breached=True).count()

        # Group tickets by priority
        by_priority = dict(
            Ticket.objects.values("priority")
            .annotate(total=Count("id"))
            .values_list("priority", "total")
        )

        # Group tickets by status
        by_status = dict(
            Ticket.objects.values("status")
            .annotate(total=Count("id"))
            .values_list("status", "total")
        )

        # Average first response time in seconds for responded tickets
        responded_tickets = Ticket.objects.filter(first_responded_at__isnull=False).annotate(
            resp_duration=ExpressionWrapper(
                F("first_responded_at") - F("created_at"),
                output_field=DurationField(),
            )
        )
        avg_resp = responded_tickets.aggregate(avg=Avg("resp_duration"))["avg"]
        avg_response_minutes = round(avg_resp.total_seconds() / 60, 2) if avg_resp else None

        # Active agent workload (unresolved tickets per agent)
        agent_workload = list(
            User.objects.filter(role__in=[User.Role.AGENT, User.Role.MANAGER])
            .annotate(
                active_tickets=Count(
                    "assigned_tickets",
                    filter=~Q(assigned_tickets__status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]),
                )
            )
            .values("id", "email", "active_tickets")
            .order_by("-active_tickets")
        )

        return {
            "total_tickets": total_tickets,
            "sla_breached_count": breached_tickets,
            "tickets_by_priority": by_priority,
            "tickets_by_status": by_status,
            "avg_first_response_minutes": avg_response_minutes,
            "agent_workload": agent_workload,
        }