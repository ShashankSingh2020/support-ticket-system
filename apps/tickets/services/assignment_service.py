from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.tickets.models import Ticket, TicketAssignmentHistory, TicketEvent
from apps.users.models import User, Team


class TicketAssignmentService:
    @staticmethod
    @transaction.atomic
    def assign_ticket(*, ticket: Ticket, assigned_by: User, team: Team = None, agent: User = None) -> Ticket:
        """
        Assigns or reassigns ticket to a team and/or agent, validating agent role and team membership.
        """
        if agent:
            if agent.role not in [User.Role.AGENT, User.Role.MANAGER]:
                raise ValidationError("Only agents or managers can be assigned to tickets.")
            if team and agent.team_id and agent.team_id != team.id:
                raise ValidationError(f"Agent {agent.email} does not belong to team {team.name}.")
            if not team and agent.team:
                team = agent.team

        from_team = ticket.assigned_team
        from_agent = ticket.assigned_agent

        ticket.assigned_team = team
        ticket.assigned_agent = agent
        ticket.save(update_fields=["assigned_team", "assigned_agent", "updated_at"])

        TicketAssignmentHistory.objects.create(
            ticket=ticket,
            assigned_by=assigned_by,
            from_team=from_team,
            to_team=team,
            from_agent=from_agent,
            to_agent=agent,
        )

        TicketEvent.objects.create(
            ticket=ticket,
            actor=assigned_by,
            event_type=TicketEvent.EventType.ASSIGNMENT_CHANGED,
            old_value=f"team:{from_team.id if from_team else None}, agent:{from_agent.id if from_agent else None}",
            new_value=f"team:{team.id if team else None}, agent:{agent.id if agent else None}",
        )
        return ticket