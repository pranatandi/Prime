from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class TenantRequiredMixin(LoginRequiredMixin):
    """Scopes querysets to request.user.tenant and stamps tenant on create.

    Every CBV for a tenant-owned model should mix this in. It assumes the
    model exposes a `tenant` FK (see core.models.TenantScopedModel).
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(tenant=self.request.user.tenant)

    def form_valid(self, form):
        if hasattr(form.instance, "tenant_id"):
            form.instance.tenant = self.request.user.tenant
        return super().form_valid(form)


class RoleRequiredMixin(LoginRequiredMixin):
    """Restrict a view to specific roles. Set `allowed_roles` on the view."""

    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.allowed_roles:
            if request.user.role not in self.allowed_roles and not request.user.is_superuser:
                raise PermissionDenied("Anda tidak punya akses ke modul ini.")
        return super().dispatch(request, *args, **kwargs)
