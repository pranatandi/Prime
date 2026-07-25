from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import Tenant
from finance.models import Account, BankAccount, Payment
from inventory.models import Product, StockMovement, Warehouse
from .models import Bill, BillItem, PurchaseOrder, PurchaseOrderItem, Vendor


class PurchaseOrderWorkflowTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.user = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant, role=User.Role.ADMIN,
        )
        self.warehouse = Warehouse.objects.create(tenant=self.tenant, name="Gudang Utama")
        self.inventory_account = Account.objects.create(
            tenant=self.tenant, code="1300", name="Persediaan", type=Account.AccountType.ASSET,
        )
        self.ap_account = Account.objects.create(
            tenant=self.tenant, code="2000", name="Hutang Usaha", type=Account.AccountType.LIABILITY,
        )
        self.product = Product.objects.create(
            tenant=self.tenant, sku="SKU1", name="Produk A", cost_price=Decimal("10000"), sell_price=Decimal("15000"),
            inventory_account=self.inventory_account,
        )
        self.vendor = Vendor.objects.create(tenant=self.tenant, name="Vendor A")
        self.po = PurchaseOrder.objects.create(
            tenant=self.tenant, po_number="PO-0001", vendor=self.vendor, warehouse=self.warehouse, order_date="2026-07-01",
        )
        PurchaseOrderItem.objects.create(
            purchase_order=self.po, product=self.product, description="Produk A", quantity=10, unit_price=Decimal("12000"),
        )
        self.client.login(username="user_a", password="pass12345")

    def test_receive_adds_stock_and_posts_journal(self):
        response = self.client.post(
            reverse("purchasing:purchaseorder_receive", args=[self.po.pk]),
            {"contra_account": self.ap_account.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.po.refresh_from_db()
        self.assertEqual(self.po.status, PurchaseOrder.Status.RECEIVED)

        movement = StockMovement.objects.get(product=self.product)
        self.assertEqual(movement.quantity, Decimal("10"))
        self.assertEqual(self.product.total_stock, Decimal("10"))

        entry = self.inventory_account.lines.first().entry
        lines = list(entry.lines.all())
        inv_line = next(l for l in lines if l.account_id == self.inventory_account.pk)
        ap_line = next(l for l in lines if l.account_id == self.ap_account.pk)
        self.assertEqual(inv_line.debit, Decimal("120000"))
        self.assertEqual(ap_line.credit, Decimal("120000"))

    def test_create_bill_from_purchase_order(self):
        self.client.post(
            reverse("purchasing:purchaseorder_receive", args=[self.po.pk]), {"contra_account": self.ap_account.pk},
        )
        response = self.client.post(reverse("purchasing:purchaseorder_create_bill", args=[self.po.pk]))
        self.assertEqual(response.status_code, 302)
        bill = Bill.objects.get(purchase_order=self.po)
        self.assertEqual(bill.items.count(), 1)
        self.assertEqual(bill.total, self.po.total)


class BillPaymentTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.vendor = Vendor.objects.create(tenant=self.tenant, name="Vendor A")
        self.bill = Bill.objects.create(
            tenant=self.tenant, number="BILL-0001", vendor=self.vendor, bill_date="2026-07-01", due_date="2026-07-15",
        )
        BillItem.objects.create(bill=self.bill, description="Barang", quantity=1, unit_price=Decimal("100000"))

    def test_payment_reduces_balance_due(self):
        kas = Account.objects.create(tenant=self.tenant, code="1000", name="Kas", type=Account.AccountType.ASSET)
        bank = BankAccount.objects.create(tenant=self.tenant, name="Kas Utama", account=kas)
        ap = Account.objects.create(tenant=self.tenant, code="2000", name="Hutang Usaha", type=Account.AccountType.LIABILITY)
        Payment.objects.create(
            tenant=self.tenant, bank_account=bank, contra_account=ap, direction=Payment.Direction.OUT,
            date="2026-07-10", amount=Decimal("100000"), bill=self.bill,
        )
        self.bill.refresh_from_db()
        self.assertEqual(self.bill.amount_paid, Decimal("100000"))
        self.assertEqual(self.bill.balance_due, Decimal("0"))

    def test_total_idr_with_foreign_currency(self):
        self.bill.currency = "USD"
        self.bill.exchange_rate = Decimal("15000")
        self.bill.save()
        self.assertEqual(self.bill.total, Decimal("100000"))
        self.assertEqual(self.bill.total_idr, Decimal("1500000000"))


class PurchaseOrderTenantIsolationTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A")
        self.tenant_b = Tenant.objects.create(name="Tenant B")
        self.user_a = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant_a, role=User.Role.ADMIN,
        )
        PurchaseOrder.objects.create(tenant=self.tenant_a, po_number="PO-A", order_date="2026-07-01")
        PurchaseOrder.objects.create(tenant=self.tenant_b, po_number="PO-B", order_date="2026-07-01")
        self.client.login(username="user_a", password="pass12345")

    def test_list_only_shows_own_tenant(self):
        response = self.client.get(reverse("purchasing:purchaseorder_list"))
        self.assertContains(response, "PO-A")
        self.assertNotContains(response, "PO-B")
