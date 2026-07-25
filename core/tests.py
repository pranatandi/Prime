from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from crm.models import PipelineStage
from .models import AuditLog, Tenant


class AuditLogTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.user = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant, role=User.Role.ADMIN,
        )
        self.stage = PipelineStage.objects.create(tenant=self.tenant, name="New", order=0)
        self.client.login(username="user_a", password="pass12345")

    def test_creating_deal_writes_audit_log(self):
        response = self.client.post(reverse("crm:deal_create"), {
            "title": "Audited Deal",
            "stage": self.stage.pk,
            "value": "1000",
            "status": "OPEN",
        })
        self.assertEqual(response.status_code, 302)
        log = AuditLog.objects.filter(model_name="Deal", action=AuditLog.Action.CREATE).latest("changed_at")
        self.assertEqual(log.tenant, self.tenant)
        self.assertEqual(log.user, self.user)
        self.assertIn("Audited Deal", log.object_repr)
