from django.contrib import admin

from core.admin import TenantScopedAdmin
from .models import Activity, Company, Contact, Deal, PipelineStage


@admin.register(Company)
class CompanyAdmin(TenantScopedAdmin):
    list_display = ("name", "industry", "phone", "owner", "tenant")
    list_filter = ("tenant",)
    search_fields = ("name",)


@admin.register(Contact)
class ContactAdmin(TenantScopedAdmin):
    list_display = ("full_name", "company", "email", "phone", "tenant")
    list_filter = ("tenant",)
    search_fields = ("first_name", "last_name", "email")


@admin.register(PipelineStage)
class PipelineStageAdmin(TenantScopedAdmin):
    list_display = ("name", "order", "is_won", "is_lost", "tenant")
    list_filter = ("tenant",)


@admin.register(Deal)
class DealAdmin(TenantScopedAdmin):
    list_display = ("title", "company", "stage", "value", "status", "owner", "tenant")
    list_filter = ("tenant", "status", "stage")
    search_fields = ("title",)


@admin.register(Activity)
class ActivityAdmin(TenantScopedAdmin):
    list_display = ("subject", "type", "due_date", "is_done", "assigned_to", "tenant")
    list_filter = ("tenant", "type", "is_done")
