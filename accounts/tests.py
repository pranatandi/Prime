from django.test import TestCase
from django.urls import reverse

from core.models import Tenant
from .models import User


class SignupTests(TestCase):
    def test_signup_creates_tenant_and_admin_user(self):
        response = self.client.post(reverse("signup"), {
            "company_name": "Test Company",
            "username": "testadmin",
            "first_name": "Test",
            "last_name": "Admin",
            "email": "admin@test.com",
            "password1": "SuperSecret123!",
            "password2": "SuperSecret123!",
        })
        self.assertEqual(response.status_code, 302)

        tenant = Tenant.objects.get(name="Test Company")
        user = User.objects.get(username="testadmin")
        self.assertEqual(user.tenant, tenant)
        self.assertEqual(user.role, User.Role.ADMIN)

        # The user should be logged in automatically after signup.
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)

    def test_signup_rejects_duplicate_company_name(self):
        Tenant.objects.create(name="Existing Co")
        response = self.client.post(reverse("signup"), {
            "company_name": "Existing Co",
            "username": "another",
            "first_name": "A",
            "email": "a@test.com",
            "password1": "SuperSecret123!",
            "password2": "SuperSecret123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="another").exists())


class TenantSettingsAccessTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.admin = User.objects.create_user(
            username="admin_a", password="pass12345", tenant=self.tenant, role=User.Role.ADMIN,
        )
        self.staff = User.objects.create_user(
            username="staff_a", password="pass12345", tenant=self.tenant, role=User.Role.STAFF,
        )

    def test_admin_can_access_settings(self):
        self.client.login(username="admin_a", password="pass12345")
        response = self.client.get(reverse("accounts:settings"))
        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_access_settings(self):
        self.client.login(username="staff_a", password="pass12345")
        response = self.client.get(reverse("accounts:settings"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_update_company_profile(self):
        self.client.login(username="admin_a", password="pass12345")
        response = self.client.post(reverse("accounts:settings"), {
            "name": "Tenant A",
            "address": "Jl. Sudirman No. 1",
            "phone": "021-1234567",
        })
        self.assertEqual(response.status_code, 302)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.address, "Jl. Sudirman No. 1")
