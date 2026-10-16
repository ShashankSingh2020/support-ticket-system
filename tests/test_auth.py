import pytest
from rest_framework import status
from apps.users.models import User


@pytest.mark.django_db
class TestAuthentication:
    def test_customer_registration(self, api_client):
        payload = {
            "email": "newbie@example.com",
            "password": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User",
        }
        res = api_client.post("/api/v1/users/auth/register/", data=payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data["email"] == "newbie@example.com"

        user = User.objects.get(email="newbie@example.com")
        assert user.role == User.Role.CUSTOMER

    def test_login_and_token_retrieval(self, api_client, customer_user):
        payload = {
            "email": customer_user.email,
            "password": "TestPassword123!",
        }
        res = api_client.post("/api/v1/users/auth/login/", data=payload, format="json")
        assert res.status_code == status.HTTP_200_OK
        assert "access" in res.data
        assert "refresh" in res.data
        assert res.data["user"]["role"] == User.Role.CUSTOMER

    def test_profile_endpoint_requires_token(self, api_client):
        res = api_client.get("/api/v1/users/auth/me/")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_endpoint_success(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        res = api_client.get("/api/v1/users/auth/me/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["email"] == customer_user.email