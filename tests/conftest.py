import pytest
from rest_framework.test import APIClient
from apps.users.models import User, Team
from apps.tickets.models import SLAPolicy


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sla_policies(db):
    policies = [
        ("CRITICAL", 30, 240),
        ("HIGH", 120, 480),
        ("MEDIUM", 480, 1440),
        ("LOW", 1440, 2880),
    ]
    created = []
    for priority, resp, resol in policies:
        p, _ = SLAPolicy.objects.get_or_create(
            priority=priority,
            defaults={
                "name": f"{priority} Test SLA",
                "first_response_time_minutes": resp,
                "resolution_time_minutes": resol,
            },
        )
        created.append(p)
    return created


@pytest.fixture
def support_team(db):
    return Team.objects.create(name="Support Tier 1", description="General customer support")


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        email="customer_test@example.com",
        password="TestPassword123!",
        role=User.Role.CUSTOMER,
        first_name="Customer",
        last_name="One",
    )


@pytest.fixture
def second_customer(db):
    return User.objects.create_user(
        email="customer_two@example.com",
        password="TestPassword123!",
        role=User.Role.CUSTOMER,
        first_name="Customer",
        last_name="Two",
    )


@pytest.fixture
def agent_user(db, support_team):
    return User.objects.create_user(
        email="agent_test@example.com",
        password="TestPassword123!",
        role=User.Role.AGENT,
        team=support_team,
        first_name="Agent",
        last_name="One",
    )


@pytest.fixture
def manager_user(db, support_team):
    return User.objects.create_user(
        email="manager_test@example.com",
        password="TestPassword123!",
        role=User.Role.MANAGER,
        team=support_team,
        first_name="Manager",
        last_name="One",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin_test@example.com",
        password="TestPassword123!",
        first_name="Admin",
        last_name="Super",
    )