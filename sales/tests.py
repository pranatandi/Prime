from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import Tenant
from crm.models import Company
from finance.models import Account
from inventory.models import Product, StockMovement, Warehouse
from .models import SalesOrder, SalesOrderItem


class SalesOrderWorkflowTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.user = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant, role=User.Role.ADMIN,
        )
        self.warehouse = Warehouse.objects.create(tenant=self.tenant, name="Gudang Utama")
        self.inventory_account = Account.objects.create(
            tenant=self.tenant, code="1300", name="Persediaan", type=Account.AccountType.ASSET,
        )
        self.cogs_account = Account.objects.create(
            tenant=self.tenant, code="5100", name="HPP", type=Account.AccountType.EXPENSE,
        )
        self.product = Product.objects.create(
            tenant=self.tenant, sku="SKU1", name="Produk A", cost_price=Decimal("10000"), sell_price=Decimal("15000"),
            inventory_account=self.inventory_account, cogs_account=self.cogs_account,
        )
        self.company = Company.objects.create(tenant=self.tenant, name="Customer A")
        self.so = SalesOrder.objects.create(
            tenant=self.tenant, so_number="SO-0001", customer=self.company, warehouse=self.warehouse,
            order_date="2026-07-01",
        )
        SalesOrderItem.objects.create(
            sales_order=self.so, product=self.product, description="Produk A", quantity=5, unit_price=Decimal("15000"),
        )
        self.client.login(username="user_a", password="pass12345")

    def test_deliver_deducts_stock_and_posts_cogs(self):
        response = self.client.post(reverse("sales:salesorder_deliver", args=[self.so.pk]))
        self.assertEqual(response.status_code, 302)
        self.so.refresh_from_db()
        self.assertEqual(self.so.status, SalesOrder.Status.DELIVERED)

        movement = StockMovement.objects.get(product=self.product)
        self.assertEqual(movement.quantity, Decimal("-5"))
        self.assertEqual(self.product.total_stock, Decimal("-5"))

        entry = self.cogs_account.lines.first().entry
        lines = list(entry.lines.all())
        self.assertEqual(len(lines), 2)
        cogs_line = next(l for l in lines if l.account_id == self.cogs_account.pk)
        inv_line = next(l for l in lines if l.account_id == self.inventory_account.pk)
        self.assertEqual(cogs_line.debit, Decimal("50000"))
        self.assertEqual(inv_line.credit, Decimal("50000"))

    def test_create_invoice_from_sales_order(self):
        self.client.post(reverse("sales:salesorder_deliver", args=[self.so.pk]))
        response = self.client.post(reverse("sales:salesorder_create_invoice", args=[self.so.pk]))
        self.assertEqual(response.status_code, 302)
        self.so.refresh_from_db()
        self.assertEqual(self.so.status, SalesOrder.Status.INVOICED)
        self.assertIsNotNone(self.so.invoice)
        self.assertEqual(self.so.invoice.items.count(), 1)
        self.assertEqual(self.so.invoice.total, self.so.total)


class SalesOrderTenantIsolationTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A")
        self.tenant_b = Tenant.objects.create(name="Tenant B")
        self.user_a = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant_a, role=User.Role.ADMIN,
        )
        SalesOrder.objects.create(tenant=self.tenant_a, so_number="SO-A", order_date="2026-07-01")
        SalesOrder.objects.create(tenant=self.tenant_b, so_number="SO-B", order_date="2026-07-01")
        self.client.login(username="user_a", password="pass12345")

    def test_list_only_shows_own_tenant(self):
        response = self.client.get(reverse("sales:salesorder_list"))
        self.assertContains(response, "SO-A")
        self.assertNotContains(response, "SO-B")
