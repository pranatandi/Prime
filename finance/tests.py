from decimal import Decimal

from django.test import TestCase

from core.models import Tenant
from .models import Invoice, InvoiceItem, TaxRate


class InvoiceTotalTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.tax = TaxRate.objects.create(tenant=self.tenant, name="PPN", rate=Decimal("11"))
        self.invoice = Invoice.objects.create(
            tenant=self.tenant, number="INV-1", issue_date="2026-07-01", due_date="2026-07-15",
        )

    def test_totals_with_tax(self):
        InvoiceItem.objects.create(
            invoice=self.invoice, description="Item 1", quantity=2, unit_price=Decimal("100000"), tax_rate=self.tax,
        )
        InvoiceItem.objects.create(
            invoice=self.invoice, description="Item 2 (no tax)", quantity=1, unit_price=Decimal("50000"),
        )
        self.assertEqual(self.invoice.subtotal, Decimal("250000"))
        self.assertEqual(self.invoice.tax_total, Decimal("22000"))
        self.assertEqual(self.invoice.total, Decimal("272000"))

    def test_totals_with_no_items(self):
        self.assertEqual(self.invoice.subtotal, Decimal("0"))
        self.assertEqual(self.invoice.total, Decimal("0"))
