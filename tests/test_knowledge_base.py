import pytest
from rest_framework import status
from apps.knowledge_base.models import Article


@pytest.mark.django_db
class TestKnowledgeBase:
    def test_unauthenticated_and_customers_only_see_published(
        self, api_client, customer_user, manager_user
    ):
        # Create published article
        Article.objects.create(
            title="How to reset password",
            slug="how-to-reset-password",
            content="Click forgot password link on the login page.",
            category="Auth",
            status=Article.Status.PUBLISHED,
            author=manager_user,
        )

        # Create draft article
        Article.objects.create(
            title="Internal Staff Onboarding",
            slug="internal-staff-onboarding",
            content="Steps for staff members only.",
            category="Internal",
            status=Article.Status.DRAFT,
            author=manager_user,
        )

        # Unauthenticated query
        res = api_client.get("/api/v1/kb/articles/")
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]["slug"] == "how-to-reset-password"

        # Customer query
        api_client.force_authenticate(user=customer_user)
        res_cust = api_client.get("/api/v1/kb/articles/")
        assert len(res_cust.data) == 1

        # Manager query sees both
        api_client.force_authenticate(user=manager_user)
        res_mgr = api_client.get("/api/v1/kb/articles/")
        assert len(res_mgr.data) == 2