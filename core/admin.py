from django.contrib import admin

from .models import Tenant


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
