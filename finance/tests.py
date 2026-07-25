from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import Tenant
from .models import Account, BankAccount, Invoice, InvoiceItem, Payment, TaxRate


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


class PaymentTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.kas = Account.objects.create(tenant=self.tenant, code="1000", name="Kas", type=Account.AccountType.ASSET)
        self.ar = Account.objects.create(tenant=self.tenant, code="1100", name="Piutang Usaha", type=Account.AccountType.ASSET)
        self.expense = Account.objects.create(tenant=self.tenant, code="5000", name="Beban Operasional", type=Account.AccountType.EXPENSE)
        self.bank = BankAccount.objects.create(tenant=self.tenant, name="Kas Utama", account=self.kas)
        self.invoice = Invoice.objects.create(
            tenant=self.tenant, number="INV-1", issue_date="2026-07-01", due_date="2026-07-15",
        )
        InvoiceItem.objects.create(invoice=self.invoice, description="Jasa", quantity=1, unit_price=Decimal("100000"))

    def test_payment_in_posts_journal_entry_and_reduces_balance_due(self):
        payment = Payment.objects.create(
            tenant=self.tenant, bank_account=self.bank, contra_account=self.ar,
            direction=Payment.Direction.IN, date="2026-07-05", amount=Decimal("100000"),
            invoice=self.invoice,
        )
        self.assertIsNotNone(payment.journal_entry)
        lines = list(payment.journal_entry.lines.all())
        self.assertEqual(len(lines), 2)
        kas_line = next(line for line in lines if line.account == self.kas)
        ar_line = next(line for line in lines if line.account == self.ar)
        self.assertEqual(kas_line.debit, Decimal("100000"))
        self.assertEqual(ar_line.credit, Decimal("100000"))

        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount_paid, Decimal("100000"))
        self.assertEqual(self.invoice.balance_due, Decimal("0"))

    def test_payment_out_posts_opposite_journal_entry(self):
        payment = Payment.objects.create(
            tenant=self.tenant, bank_account=self.bank, contra_account=self.expense,
            direction=Payment.Direction.OUT, date="2026-07-06", amount=Decimal("25000"),
        )
        lines = list(payment.journal_entry.lines.all())
        kas_line = next(line for line in lines if line.account == self.kas)
        expense_line = next(line for line in lines if line.account == self.expense)
        self.assertEqual(kas_line.credit, Decimal("25000"))
        self.assertEqual(expense_line.debit, Decimal("25000"))


class BalanceSheetTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.user = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant, role=User.Role.ADMIN,
        )
        self.kas = Account.objects.create(tenant=self.tenant, code="1000", name="Kas", type=Account.AccountType.ASSET)
        self.modal = Account.objects.create(tenant=self.tenant, code="3000", name="Modal", type=Account.AccountType.EQUITY)
        self.bank = BankAccount.objects.create(tenant=self.tenant, name="Kas Utama", account=self.kas)
        Payment.objects.create(
            tenant=self.tenant, bank_account=self.bank, contra_account=self.modal,
            direction=Payment.Direction.IN, date="2026-07-01", amount=Decimal("1000000"),
        )
        self.client.login(username="user_a", password="pass12345")

    def test_balance_sheet_balances(self):
        response = self.client.get(reverse("finance:balance_sheet"), {"as_of": "2026-07-31"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_assets"], Decimal("1000000"))
        self.assertEqual(response.context["total_liabilities_equity"], Decimal("1000000"))


class FinanceTenantIsolationTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A")
        self.tenant_b = Tenant.objects.create(name="Tenant B")
        self.user_a = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant_a, role=User.Role.ADMIN,
        )
        kas_a = Account.objects.create(tenant=self.tenant_a, code="1000", name="Kas A", type=Account.AccountType.ASSET)
        kas_b = Account.objects.create(tenant=self.tenant_b, code="1000", name="Kas B", type=Account.AccountType.ASSET)
        BankAccount.objects.create(tenant=self.tenant_a, name="Bank A", account=kas_a)
        BankAccount.objects.create(tenant=self.tenant_b, name="Bank B", account=kas_b)
        self.client.login(username="user_a", password="pass12345")

    def test_bank_account_list_only_shows_own_tenant(self):
        response = self.client.get(reverse("finance:bankaccount_list"))
        self.assertContains(response, "Bank A")
        self.assertNotContains(response, "Bank B")
