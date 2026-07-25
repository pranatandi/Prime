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

    @property
    def amount_paid(self):
        return sum(
            (p.amount for p in self.payments.filter(direction=Payment.Direction.IN)), Decimal("0")
        )

    @property
    def balance_due(self):
        return self.total - self.amount_paid


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


class BankAccount(TenantScopedModel):
    name = models.CharField(max_length=150)
    account = models.OneToOneField(Account, on_delete=models.PROTECT, related_name="bank_account")
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    is_cash = models.BooleanField(default=False, help_text="Centang untuk kas tunai (bukan rekening bank).")
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def book_balance(self):
        lines = JournalEntryLine.objects.filter(entry__tenant=self.tenant, account=self.account)
        totals = lines.aggregate(debit=models.Sum("debit"), credit=models.Sum("credit"))
        debit = totals["debit"] or Decimal("0")
        credit = totals["credit"] or Decimal("0")
        return self.opening_balance + debit - credit

    @property
    def reconciled_balance(self):
        payments = self.payments.filter(is_reconciled=True)
        total_in = sum((p.amount for p in payments.filter(direction=Payment.Direction.IN)), Decimal("0"))
        total_out = sum((p.amount for p in payments.filter(direction=Payment.Direction.OUT)), Decimal("0"))
        return self.opening_balance + total_in - total_out


class Payment(TenantScopedModel):
    class Direction(models.TextChoices):
        IN = "IN", "Uang Masuk"
        OUT = "OUT", "Uang Keluar"

    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="payments")
    contra_account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="+",
        help_text="Akun lawan, mis. Piutang Usaha (pembayaran customer) atau Beban (pengeluaran).",
    )
    direction = models.CharField(max_length=3, choices=Direction.choices)
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    bill = models.ForeignKey(
        "purchasing.Bill", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments",
    )
    memo = models.CharField(max_length=255, blank=True)
    is_reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.get_direction_display()} Rp{self.amount} - {self.bank_account}"

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating and not self.journal_entry_id:
            self._post_journal_entry()

    def _post_journal_entry(self):
        label = self.memo or f"Pembayaran {self.get_direction_display()}"
        entry = JournalEntry.objects.create(
            tenant=self.tenant, date=self.date, memo=f"{label} ({self.bank_account.name})",
        )
        if self.direction == self.Direction.IN:
            JournalEntryLine.objects.create(entry=entry, account=self.bank_account.account, debit=self.amount)
            JournalEntryLine.objects.create(entry=entry, account=self.contra_account, credit=self.amount)
        else:
            JournalEntryLine.objects.create(entry=entry, account=self.bank_account.account, credit=self.amount)
            JournalEntryLine.objects.create(entry=entry, account=self.contra_account, debit=self.amount)
        Payment.objects.filter(pk=self.pk).update(journal_entry=entry)
        self.journal_entry = entry
