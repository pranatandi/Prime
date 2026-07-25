from django.contrib import admin

from .models import AuditLog, Tenant


class TenantScopedAdmin(admin.ModelAdmin):
    """Restricts non-superusers to rows belonging to their own tenant."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(tenant=request.user.tenant)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and hasattr(obj, "tenant_id"):
            obj.tenant = request.user.tenant
        super().save_model(request, obj, form, change)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name",)


@admin.register(AuditLog)
class AuditLogAdmin(TenantScopedAdmin):
    list_display = ("changed_at", "action", "model_name", "object_repr", "user", "tenant")
    list_filter = ("tenant", "action", "model_name")
    search_fields = ("object_repr",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
