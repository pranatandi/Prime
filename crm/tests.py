from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import Tenant
from .models import Company, Deal, PipelineStage


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A")
        self.tenant_b = Tenant.objects.create(name="Tenant B")
        self.user_a = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant_a, role=User.Role.ADMIN,
        )
        self.user_b = User.objects.create_user(
            username="user_b", password="pass12345", tenant=self.tenant_b, role=User.Role.ADMIN,
        )
        self.company_a = Company.objects.create(tenant=self.tenant_a, name="Company A")
        self.company_b = Company.objects.create(tenant=self.tenant_b, name="Company B")

    def test_user_only_sees_own_tenant_companies(self):
        self.client.login(username="user_a", password="pass12345")
        response = self.client.get(reverse("crm:company_list"))
        self.assertContains(response, "Company A")
        self.assertNotContains(response, "Company B")

    def test_user_cannot_edit_other_tenant_company(self):
        self.client.login(username="user_a", password="pass12345")
        response = self.client.get(reverse("crm:company_edit", args=[self.company_b.pk]))
        self.assertEqual(response.status_code, 404)

    def test_csv_export_only_includes_own_tenant_data(self):
        self.client.login(username="user_a", password="pass12345")
        response = self.client.get(reverse("crm:company_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        body = response.content.decode()
        self.assertIn("Company A", body)
        self.assertNotIn("Company B", body)


class DealCRUDTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.user = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant, role=User.Role.ADMIN,
        )
        self.stage = PipelineStage.objects.create(tenant=self.tenant, name="New", order=0)
        self.client.login(username="user_a", password="pass12345")

    def test_create_deal_stamps_tenant_automatically(self):
        response = self.client.post(reverse("crm:deal_create"), {
            "title": "Big Deal",
            "stage": self.stage.pk,
            "value": "1000000",
            "status": Deal.Status.OPEN,
        })
        self.assertEqual(response.status_code, 302)
        deal = Deal.objects.get(title="Big Deal")
        self.assertEqual(deal.tenant, self.tenant)

    def test_move_deal_to_stage(self):
        deal = Deal.objects.create(tenant=self.tenant, title="Deal 1", stage=self.stage, value=500)
        other_stage = PipelineStage.objects.create(tenant=self.tenant, name="Won", order=1, is_won=True)
        response = self.client.post(
            reverse("crm:deal_move", args=[deal.pk]),
            data='{"stage_id": %d}' % other_stage.pk,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        deal.refresh_from_db()
        self.assertEqual(deal.stage, other_stage)
        self.assertEqual(deal.status, Deal.Status.WON)
