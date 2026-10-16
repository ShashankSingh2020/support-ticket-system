from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users.models import User, Team
from apps.users.permissions import IsAdminUserRole
from apps.users.serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    TeamSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Endpoint for user login returning JWT tokens and user metadata."""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterCustomerView(generics.CreateAPIView):
    """Public endpoint for customer self-registration."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class CurrentUserProfileView(generics.RetrieveAPIView):
    """Endpoint to inspect the authenticated user's own profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class TeamViewSet(viewsets.ModelViewSet):
    """Team management reserved strictly for Admins."""
    queryset = Team.objects.all().prefetch_related("members")
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUserRole]