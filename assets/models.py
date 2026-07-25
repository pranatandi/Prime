from decimal import Decimal

from django.db import models

from core.models import TenantScopedModel
from finance.models import Account, JournalEntry


class FixedAsset(TenantScopedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        FULLY_DEPRECIATED = "FULLY_DEPRECIATED", "Fully Depreciated"
        DISPOSED = "DISPOSED", "Disposed"

    asset_number = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100, blank=True)
    acquisition_date = models.DateField()
    acquisition_cost = models.DecimalField(max_digits=14, decimal_places=2)
    salvage_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    useful_life_months = models.PositiveIntegerField(help_text="Umur manfaat dalam bulan.")
    asset_account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="+", help_text="Akun aset tetap (mis. Peralatan Kantor).",
    )
    accumulated_depreciation_account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="+",
        help_text="Akun kontra-aset akumulasi penyusutan.",
    )
    depreciation_expense_account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="+", help_text="Akun beban penyusutan.",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    disposal_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["asset_number"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "asset_number"], name="unique_asset_number_per_tenant"),
        ]

    def __str__(self):
        return f"{self.asset_number} - {self.name}"

    @property
    def monthly_depreciation(self):
        depreciable_base = self.acquisition_cost - self.salvage_value
        if self.useful_life_months <= 0 or depreciable_base <= 0:
            return Decimal("0")
        return (depreciable_base / self.useful_life_months).quantize(Decimal("0.01"))

    @property
    def accumulated_depreciation(self):
        return self.depreciation_entries.aggregate(s=models.Sum("amount"))["s"] or Decimal("0")

    @property
    def book_value(self):
        return self.acquisition_cost - self.accumulated_depreciation


class DepreciationEntry(models.Model):
    fixed_asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, related_name="depreciation_entries")
    period = models.DateField(help_text="Tanggal 1 dari bulan yang diposting.")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-period"]
        constraints = [
            models.UniqueConstraint(fields=["fixed_asset", "period"], name="unique_depreciation_per_period"),
        ]

    def __str__(self):
        return f"{self.fixed_asset} - {self.period}"
