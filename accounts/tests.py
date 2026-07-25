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
