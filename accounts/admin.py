from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from core.admin import TenantScopedAdmin
from .models import User


@admin.register(User)
class UserAdmin(TenantScopedAdmin, DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "tenant", "role", "is_active")
    list_filter = ("tenant", "role", "is_active")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Tenant", {"fields": ("tenant", "role")}),
    )
