from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import Tenant
from .models import Product


class ProductTenantIsolationTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A")
        self.tenant_b = Tenant.objects.create(name="Tenant B")
        self.user_a = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant_a, role=User.Role.ADMIN,
        )
        Product.objects.create(tenant=self.tenant_a, sku="A-1", name="Product A")
        Product.objects.create(tenant=self.tenant_b, sku="B-1", name="Product B")
        self.client.login(username="user_a", password="pass12345")

    def test_list_only_shows_own_tenant(self):
        response = self.client.get(reverse("inventory:product_list"))
        self.assertContains(response, "Product A")
        self.assertNotContains(response, "Product B")
