from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import Tenant


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SALES = "SALES", "Sales"
        FINANCE = "FINANCE", "Finance"
        HR = "HR", "HR"
        STAFF = "STAFF", "Staff"

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="users", null=True, blank=True
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)

    def __str__(self):
        return self.get_full_name() or self.username
