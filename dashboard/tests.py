from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import Tenant
from crm.models import Company


class GlobalSearchTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A")
        self.tenant_b = Tenant.objects.create(name="Tenant B")
        self.user_a = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant_a, role=User.Role.ADMIN,
        )
        Company.objects.create(tenant=self.tenant_a, name="Acme Widgets")
        Company.objects.create(tenant=self.tenant_b, name="Acme Gadgets")
        self.client.login(username="user_a", password="pass12345")

    def test_search_only_returns_own_tenant_results(self):
        response = self.client.get(reverse("dashboard:search"), {"q": "Acme"})
        self.assertContains(response, "Acme Widgets")
        self.assertNotContains(response, "Acme Gadgets")
