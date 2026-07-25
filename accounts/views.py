from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from core.mixins import RoleRequiredMixin
from core.models import AuditLog, Tenant
from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
)
from .forms import SignupForm, TenantSettingsForm, TenantUserForm
from .models import User


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Selamat datang! Perusahaan Anda berhasil didaftarkan.")
        return response


class UserListView(RoleRequiredMixin, GenericTenantListView):
    model = User
    allowed_roles = (User.Role.ADMIN,)
    title = "Pengguna"
    url_basename = "accounts:user"
    list_fields = [
        ("Username", "username"),
        ("Nama", "get_full_name"),
        ("Email", "email"),
        ("Role", "get_role_display"),
        ("Aktif", "is_active"),
    ]


class UserCreateView(RoleRequiredMixin, GenericTenantCreateView):
    model = User
    form_class = TenantUserForm
    allowed_roles = (User.Role.ADMIN,)
    title = "Pengguna"
    url_basename = "accounts:user"


class UserUpdateView(RoleRequiredMixin, GenericTenantUpdateView):
    model = User
    form_class = TenantUserForm
    allowed_roles = (User.Role.ADMIN,)
    title = "Pengguna"
    url_basename = "accounts:user"


class UserDeleteView(RoleRequiredMixin, GenericTenantDeleteView):
    model = User
    allowed_roles = (User.Role.ADMIN,)
    title = "Pengguna"
    url_basename = "accounts:user"


class TenantSettingsView(RoleRequiredMixin, UpdateView):
    """Admin-only: edit the current tenant's company profile."""

    model = Tenant
    form_class = TenantSettingsForm
    template_name = "accounts/settings.html"
    allowed_roles = (User.Role.ADMIN,)
    success_url = reverse_lazy("accounts:settings")

    def get_object(self, queryset=None):
        return self.request.user.tenant

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profil perusahaan berhasil diperbarui.")
        return response


class AuditLogListView(RoleRequiredMixin, GenericTenantListView):
    model = AuditLog
    allowed_roles = (User.Role.ADMIN,)
    title = "Audit Log"
    url_basename = "accounts:auditlog"
    readonly = True
    list_fields = [
        ("Waktu", "changed_at"), ("Aksi", "get_action_display"), ("Model", "model_name"),
        ("Objek", "object_repr"), ("Oleh", "user"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("user")
