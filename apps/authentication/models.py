import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone_number: str, password: str | None = None, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number is required.")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password) if password else user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=50, blank=True, null=True)
    platform = models.CharField(max_length=30, blank=True, null=True)
    credit_limit = models.PositiveIntegerField(default=3)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    class Meta:
        db_table = "users_user"

    @property
    def is_profile_complete(self) -> bool:
        return all((self.company_name, self.industry, self.platform))

    def __str__(self) -> str:
        return self.phone_number
