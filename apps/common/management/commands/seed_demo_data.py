from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import User, Team
from apps.tickets.models import SLAPolicy, Ticket
from apps.knowledge_base.models import Article
from apps.tickets.services.workflow_service import TicketWorkflowService


class Command(BaseCommand):
    help = "Seeds database with baseline SLA policies, teams, role-specific accounts, and sample tickets."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding baseline SLA policies...")
        sla_defaults = [
            ("CRITICAL", 30, 240),
            ("HIGH", 120, 480),
            ("MEDIUM", 480, 1440),
            ("LOW", 1440, 2880),
        ]
        for priority, resp, resol in sla_defaults:
            SLAPolicy.objects.get_or_create(
                priority=priority,
                defaults={
                    "name": f"{priority} Default SLA",
                    "first_response_time_minutes": resp,
                    "resolution_time_minutes": resol,
                },
            )

        self.stdout.write("Seeding operational teams...")
        support_team, _ = Team.objects.get_or_create(
            name="Tier 1 Support",
            defaults={"description": "General user inquiries and triaging"},
        )
        infra_team, _ = Team.objects.get_or_create(
            name="Infrastructure & DevOps",
            defaults={"description": "System outages, database failures, and scaling"},
        )

        self.stdout.write("Seeding role-based user accounts (Password: TestPass123!)...")
        users_to_create = [
            ("admin@system.local", User.Role.ADMIN, None, True, True),
            ("manager@system.local", User.Role.MANAGER, support_team, False, False),
            ("agent@system.local", User.Role.AGENT, support_team, False, False),
            ("customer@client.local", User.Role.CUSTOMER, None, False, False),
        ]

        created_users = {}
        for email, role, team, is_staff, is_super in users_to_create:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "role": role,
                    "team": team,
                    "is_staff": is_staff,
                    "is_superuser": is_super,
                    "first_name": role.capitalize(),
                    "last_name": "User",
                },
            )
            if created:
                user.set_password("TestPass123!")
                user.save()
            created_users[role] = user

        self.stdout.write("Seeding knowledge base articles...")
        Article.objects.get_or_create(
            slug="how-to-reset-password",
            defaults={
                "title": "How to Reset Your Account Password",
                "category": "Authentication",
                "status": Article.Status.PUBLISHED,
                "author": created_users[User.Role.ADMIN],
                "content": "Navigate to /auth/login and select 'Forgot Password' to receive a recovery token.",
            },
        )
        Article.objects.get_or_create(
            slug="agent-playbook-sla-escalations",
            defaults={
                "title": "Internal SLA Escalation Guidelines",
                "category": "Operations",
                "status": Article.Status.DRAFT,
                "author": created_users[User.Role.MANAGER],
                "content": "If a Critical ticket reaches 50% of response time without assignment, escalate in the priority channel.",
            },
        )

        self.stdout.write("Seeding sample tickets...")
        customer = created_users[User.Role.CUSTOMER]
        if not Ticket.objects.filter(customer=customer).exists():
            TicketWorkflowService.create_ticket(
                customer=customer,
                title="VPN access failure",
                description="Unable to connect to the internal VPN from remote network.",
                category="Infrastructure",
                priority=Ticket.Priority.HIGH,
            )

        self.stdout.write(self.style.SUCCESS("Demo environment seeded successfully!"))