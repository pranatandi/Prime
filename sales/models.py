from decimal import Decimal

from django.db import models

from core.models import TenantScopedModel
from crm.models import Company
from finance.models import Invoice, TaxRate
from inventory.models import Product, Warehouse


class SalesOrder(TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        CONFIRMED = "CONFIRMED", "Confirmed"
        DELIVERED = "DELIVERED", "Delivered"
        INVOICED = "INVOICED", "Invoiced"
        CANCELLED = "CANCELLED", "Cancelled"

    so_number = models.CharField(max_length=50)
    customer = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_orders")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_orders")
    order_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-order_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "so_number"], name="unique_so_number_per_tenant"),
        ]

    def __str__(self):
        return self.so_number

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0"))

    @property
    def tax_total(self):
        return sum((item.tax_amount for item in self.items.all()), Decimal("0"))

    @property
    def total(self):
        return self.subtotal + self.tax_total


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
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
