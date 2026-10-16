from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User, Team


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Injects user role and identity directly into the JWT token payload and response."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "role": self.user.role,
            "team": self.user.team.name if self.user.team else None,
        }
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Customer registration serializer. Disallows self-assigning privileged roles."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=User.Role.CUSTOMER,  # Hardcoded: customers cannot register as agents/managers
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Profile serializer for viewing current authenticated user details."""
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "team", "team_name")
        read_only_fields = ("id", "email", "role", "team", "team_name")


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for administrative team management."""
    member_count = serializers.IntegerField(source="members.count", read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "description", "member_count", "created_at")