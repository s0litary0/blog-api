from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db.models import EmailField, CharField, BooleanField


class CustomUserManager(BaseUserManager):
    """Custom UserManager"""

    def _create_user(self, email: str | None, password: str | None, **kwargs) -> ...:
        if not email:
            raise ValueError("You haven't provided an email")
        if not password:
            raise ValueError("You haven't provided a password")
        email_normalized: str = self.normalize_email(email=email)
        user = self.model(email=email_normalized, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(
        self, email: str | None = None, password: str | None = None, **kwargs
    ) -> ...:
        kwargs.setdefault("is_staff", False)
        kwargs.setdefault("is_superuser", False)
        return self._create_user(email=email, password=password, **kwargs)

    def create_superuser(
        self, email: str | None = None, password: str | None = None, **kwargs
    ) -> ...:
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return self._create_user(email=email, password=password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model"""

    MAX_FIRST_NAME_LENGTH: int = 50
    MAX_LAST_NAME_LENGTH: int = 50

    email = EmailField(unique=True)
    first_name = CharField(
        max_length=MAX_FIRST_NAME_LENGTH,
    )
    last_name = CharField(
        max_length=MAX_LAST_NAME_LENGTH,
    )
    is_active = BooleanField(default=True)
    is_superuser = BooleanField(default=False)
    is_staff = BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        # constraints = [
        #     UniqueConstraint(fields=("email"), name="unique_email"),
        # ]

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self) -> str:
        return self.first_name or self.email.split("@")[0]
