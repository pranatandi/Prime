from decimal import Decimal

from django.db import models

from core.models import Currency, TenantScopedModel
from finance.models import Payment, TaxRate
from inventory.models import Product, Warehouse


class Vendor(TenantScopedModel):
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PurchaseOrder(TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SENT = "SENT", "Sent"
        RECEIVED = "RECEIVED", "Received"
        CANCELLED = "CANCELLED", "Cancelled"

    po_number = models.CharField(max_length=50)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="purchase_orders")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="purchase_orders")
    order_date = models.DateField()
    expected_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-order_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "po_number"], name="unique_po_number_per_tenant"),
        ]

    def __str__(self):
        return self.po_number

    @property
    def total(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0"))


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return self.description

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class Bill(TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        RECEIVED = "RECEIVED", "Received"
        PAID = "PAID", "Paid"
        OVERDUE = "OVERDUE", "Overdue"

    number = models.CharField(max_length=50)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="bills")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="bills")
    bill_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.IDR)
    exchange_rate = models.DecimalField(
        max_digits=14, decimal_places=4, default=1,
        help_text="Kurs ke IDR pada tanggal transaksi. Biarkan 1 untuk bill dalam IDR.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-bill_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "number"], name="unique_bill_number_per_tenant"),
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
    def total_idr(self):
        return self.total * self.exchange_rate

    @property
    def amount_paid(self):
        return sum(
            (p.amount for p in self.payments.filter(direction=Payment.Direction.OUT)), Decimal("0")
        )

    @property
    def balance_due(self):
        return self.total - self.amount_paid


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")
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
