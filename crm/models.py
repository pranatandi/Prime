from django.conf import settings
from django.db import models

from core.models import TenantScopedModel


class Company(TenantScopedModel):
    name = models.CharField(max_length=150)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_companies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "companies"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(TenantScopedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    position = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_contacts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class PipelineStage(TenantScopedModel):
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    is_won = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Deal(TenantScopedModel):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        WON = "WON", "Won"
        LOST = "LOST", "Lost"

    title = models.CharField(max_length=150)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")
    stage = models.ForeignKey(PipelineStage, on_delete=models.PROTECT, related_name="deals")
    value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=4, choices=Status.choices, default=Status.OPEN)
    expected_close_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_deals"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Activity(TenantScopedModel):
    class Type(models.TextChoices):
        CALL = "CALL", "Call"
        EMAIL = "EMAIL", "Email"
        MEETING = "MEETING", "Meeting"
        TASK = "TASK", "Task"

    type = models.CharField(max_length=10, choices=Type.choices, default=Type.TASK)
    subject = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    due_date = models.DateField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "activities"
        ordering = ["is_done", "due_date"]

    def __str__(self):
        return self.subject
