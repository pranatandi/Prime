from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from core.forms import BootstrapModelForm
from core.models import Tenant
from .models import User


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class SignupForm(UserCreationForm):
    """Public self-service signup: creates a new Tenant + its first ADMIN user."""

    company_name = forms.CharField(max_length=150, label="Nama Perusahaan")
    first_name = forms.CharField(max_length=150, label="Nama Depan")
    last_name = forms.CharField(max_length=150, label="Nama Belakang", required=False)
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ["company_name", "username", "first_name", "last_name", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_company_name(self):
        name = self.cleaned_data["company_name"]
        if Tenant.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Perusahaan dengan nama ini sudah terdaftar.")
        return name

    def save(self, commit=True):
        user = super().save(commit=False)
        tenant = Tenant.objects.create(name=self.cleaned_data["company_name"])
        user.tenant = tenant
        user.role = User.Role.ADMIN
        if commit:
            user.save()
        return user


class TenantSettingsForm(BootstrapModelForm):
    class Meta:
        model = Tenant
        fields = ["name", "address", "phone"]


class TenantUserForm(BootstrapModelForm):
    """Used by tenant admins to add/edit users within their own company."""

    password = forms.CharField(
        widget=forms.PasswordInput, required=False,
        help_text="Kosongkan jika tidak ingin mengubah password.",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "password", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tenant = self.tenant
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
