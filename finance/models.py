from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from core.models import TenantScopedModel
from crm.models import Company


class Account(TenantScopedModel):
    class AccountType(models.TextChoices):
        ASSET = "ASSET", "Asset"
        LIABILITY = "LIABILITY", "Liability"
        EQUITY = "EQUITY", "Equity"
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=10, choices=AccountType.choices)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children")

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="unique_account_code_per_tenant"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class JournalEntry(TenantScopedModel):
    date = models.DateField()
    memo = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "journal entries"
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.date} - {self.memo or self.pk}"

    @property
    def total_debit(self):
        return sum((line.debit for line in self.lines.all()), Decimal("0"))

    @property
    def total_credit(self):
        return sum((line.credit for line in self.lines.all()), Decimal("0"))


class JournalEntryLine(models.Model):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="lines")
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.account} D{self.debit}/C{self.credit}"


class TaxRate(TenantScopedModel):
    name = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], help_text="Persen, mis. 11 untuk 11%")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class Invoice(TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SENT = "SENT", "Sent"
        PAID = "PAID", "Paid"
        OVERDUE = "OVERDUE", "Overdue"

    number = models.CharField(max_length=50)
    customer = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issue_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "number"], name="unique_invoice_number_per_tenant"),
        ]

    def __str__(self):
        return self.number

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0"))

    @property
    def tax_total(self):
        return sum((item.tax_amount for item in self.items.all()), Decimal("0"))

    @property
    def total(self):
        return self.subtotal + self.tax_total


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_rate = models.ForeignKey(TaxRate, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.description

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        if self.tax_rate:
            return self.line_total * self.tax_rate.rate / Decimal("100")
        return Decimal("0")


class Budget(TenantScopedModel):
    class Period(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        QUARTERLY = "QUARTERLY", "Quarterly"
        YEARLY = "YEARLY", "Yearly"

    name = models.CharField(max_length=150)
    fiscal_year = models.PositiveIntegerField()
    period = models.CharField(max_length=10, choices=Period.choices, default=Period.YEARLY)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fiscal_year", "name"]

    def __str__(self):
        return f"{self.name} ({self.fiscal_year})"

    @property
    def total_planned(self):
        return sum((line.planned_amount for line in self.lines.all()), Decimal("0"))


class BudgetLine(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="budget_lines")
    planned_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    period_start = models.DateField()
    period_end = models.DateField()

    def __str__(self):
        return f"{self.account} - {self.planned_amount}"
