import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from apps.tickets.models import Ticket
from apps.ai_assistant.service import TicketClassificationService
from apps.tickets.services.sla_service import SLAMonitoringService
from apps.tickets.services.outage_service import OutageClusterService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def classify_ticket_task(self, ticket_id: str):
    """
    Celery background worker task for ticket AI classification.
    Runs classification, auto-applies priority, and evaluates outage clustering.
    """
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except ObjectDoesNotExist:
        logger.error(f"classify_ticket_task aborted: Ticket {ticket_id} does not exist.")
        return f"Ticket {ticket_id} not found."

    # Idempotency check: avoid duplicate execution
    if ticket.ai_status == Ticket.AIClassificationStatus.COMPLETED:
        logger.info(f"Ticket {ticket_id} already classified. Skipping.")
        return f"Ticket {ticket_id} already classified."

    try:
        result = TicketClassificationService.classify_and_apply(ticket_id)
        ticket.refresh_from_db()

        # Check for widespread outage surge and auto-reply if matched
        OutageClusterService.evaluate_and_link_outage(ticket)

        return f"Classification succeeded for {ticket_id}: category={result.category}, priority={result.priority}"
    except Exception as exc:
        logger.warning(
            f"Classification attempt {self.request.retries + 1} failed for ticket {ticket_id}: {exc}"
        )
        if self.request.retries >= self.max_retries:
            logger.error(f"Exhausted retries for ticket {ticket_id}. Permanently marking as FAILED.")
            Ticket.objects.filter(id=ticket_id).update(ai_status=Ticket.AIClassificationStatus.FAILED)
        raise exc


@shared_task
def check_sla_breaches_task():
    """Periodic Celery task checking for SLA breaches across all active tickets."""
    breached_count = SLAMonitoringService.evaluate_breaches()
    logger.info(f"SLA breach monitor evaluated: {breached_count} new tickets breached.")
    return breached_count