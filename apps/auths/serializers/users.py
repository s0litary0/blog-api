from typing import Any

from django.contrib.auth.password_validation import validate_password

from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    EmailField,
    CharField,
    ValidationError,
)

from apps.auths.models import User


class UserBaseSerializer(ModelSerializer):
    """Base Serializer for User model"""

    class Meta:
        """Meta data of the Serializer"""

        model = User
        fields = "__all__"


class UserLoginSerializer(Serializer):
    """Serializer for user login"""

    email = EmailField(required=True, max_length=User.MAX_EMAIL_LENGTH)
    password = CharField(required=True)

    class Meta:
        """Meta data of the Serializer."""

        fields = ["email", "password"]

    def validate_email(self, value: str) -> str:
        """Validate the email field"""
        return value.lower()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate the input data"""

        email: str = attrs["email"]
        password: str = attrs["password"]

        user: User | None = User.objects.filter(email=email).first()

        if not user:
            raise ValidationError(
                detail={"email": [f"User with email '{email}' does not exist."]}
            )

        if not user.check_password(password):
            raise ValidationError(detail={"password": ["Incorrect password."]})

        if not user.is_active:
            raise ValidationError(detail={"is_active": ["User is inactive."]})

        attrs["user"] = user

        return super().validate(attrs)


class UserRegisterSerializer(UserBaseSerializer):
    """Serializer for user registering"""

    class Meta(UserBaseSerializer.Meta):
        fields = ["first_name", "last_name", "email", "password"]

        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value: str) -> str:
        """Validate the email field"""
        return value.lower()

    def validate_password(self, value: str) -> str:
        """Validate the password field"""
        validate_password(value)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate the input date"""

        email: str = attrs["email"]

        user: User | None = User.objects.filter(email=email).first()

        if user is not None:
            raise ValidationError(
                detail={"email": ["An account with this email already exists."]}
            )

        return super().validate(attrs)

    def create(self, validated_data: dict[str, Any]):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )


class UserDetailSerializer(UserBaseSerializer):
    """Serializer for displaying detail User instances"""

    class Meta(UserBaseSerializer.Meta):
        """Meta data of the Serializer."""

        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            # "is_active",
            # "is_staff",
            # "is_superuser",
        ]


class UserUpdateSerializer(UserBaseSerializer):
    """Serializer for displaying detail User instances"""

    class Meta(UserBaseSerializer.Meta):
        """Meta data of the Serializer."""

        fields = ["id", "email", "first_name", "last_name"]
        read_only_fields = ["id", "email"]

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update user info"""

        if "first_name" in validated_data:
            instance.first_name = validated_data["first_name"]
        if "last_name" in validated_data:
            instance.last_name = validated_data["last_name"]

        instance.save()
        return instance