from django.db import models
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.tickets.models import Ticket, TicketReply
from apps.tickets.permissions import CanAccessTicket
from apps.users.permissions import IsStaffOrSupport
from apps.users.models import User, Team
from apps.tickets.serializers import (
    TicketSerializer,
    TicketCreateSerializer,
    TicketReplySerializer,
    TicketEventSerializer,
)
from apps.tickets.services.workflow_service import TicketWorkflowService
from apps.tickets.services.assignment_service import TicketAssignmentService
from apps.tickets.services.reply_service import TicketReplyService


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessTicket]

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.select_related("customer", "assigned_agent", "assigned_team")

        if user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return qs.all()
        if user.role == User.Role.AGENT:
            return qs.filter(
                Q(assigned_agent=user)
                | Q(assigned_team=user.team)
                | Q(assigned_team__isnull=True)
            )
        # Customer access: own tickets only
        return qs.filter(customer=user)

    def create(self, request, *args, **kwargs):
        serializer = TicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = TicketWorkflowService.create_ticket(
            customer=request.user,
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
            category=serializer.validated_data.get("category", "General"),
        )
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="transition-status")
    def transition_status(self, request, pk=None):
        ticket = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "status field is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Customers cannot mark in-progress or closed directly unless specified
        if request.user.role == User.Role.CUSTOMER and new_status not in [Ticket.Status.CLOSED]:
            return Response({"error": "Customers cannot trigger this status transition."}, status=status.HTTP_403_FORBIDDEN)

        updated_ticket = TicketWorkflowService.transition_status(
            ticket=ticket,
            new_status=new_status,
            actor=request.user,
        )
        return Response(TicketSerializer(updated_ticket).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsStaffOrSupport])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        agent_id = request.data.get("agent_id")
        team_id = request.data.get("team_id")

        agent = User.objects.filter(id=agent_id).first() if agent_id else None
        team = Team.objects.filter(id=team_id).first() if team_id else None

        updated_ticket = TicketAssignmentService.assign_ticket(
            ticket=ticket,
            assigned_by=request.user,
            team=team,
            agent=agent,
        )
        return Response(TicketSerializer(updated_ticket).data)

    @action(detail=True, methods=["get", "post"], url_path="replies")
    def replies(self, request, pk=None):
        ticket = self.get_object()

        if request.method == "GET":
            replies = ticket.replies.all()
            if request.user.role == User.Role.CUSTOMER:
                replies = replies.filter(is_internal=False)
            return Response(TicketReplySerializer(replies, many=True).data)

        content = request.data.get("content")
        is_internal = bool(request.data.get("is_internal", False))

        if not content:
            return Response({"error": "content is required."}, status=status.HTTP_400_BAD_REQUEST)

        reply = TicketReplyService.add_reply(
            ticket=ticket,
            author=request.user,
            content=content,
            is_internal=is_internal,
        )
        return Response(TicketReplySerializer(reply).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="events")
    def events(self, request, pk=None):
        ticket = self.get_object()
        return Response(TicketEventSerializer(ticket.events.all(), many=True).data)