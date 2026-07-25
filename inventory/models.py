from decimal import Decimal

from django.db import models

from core.models import TenantScopedModel


class Warehouse(TenantScopedModel):
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(TenantScopedModel):
    sku = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=20, default="pcs")
    cost_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sell_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    track_inventory = models.BooleanField(default=True)
    inventory_account = models.ForeignKey(
        "finance.Account", on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
        help_text="Akun aset persediaan. Kalau kosong, mutasi stok tidak posting ke jurnal.",
    )
    cogs_account = models.ForeignKey(
        "finance.Account", on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
        help_text="Akun beban HPP (Cost of Goods Sold).",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sku"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "sku"], name="unique_product_sku_per_tenant"),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def total_stock(self):
        return self.stock_movements.aggregate(s=models.Sum("quantity"))["s"] or Decimal("0")

    def stock_in_warehouse(self, warehouse):
        return self.stock_movements.filter(warehouse=warehouse).aggregate(
            s=models.Sum("quantity")
        )["s"] or Decimal("0")


class StockMovement(TenantScopedModel):
    class MovementType(models.TextChoices):
        RECEIPT = "RECEIPT", "Penerimaan"
        DELIVERY = "DELIVERY", "Pengiriman"
        ADJUSTMENT = "ADJUSTMENT", "Penyesuaian"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="stock_movements")
    date = models.DateField()
    quantity = models.DecimalField(
        max_digits=14, decimal_places=2, help_text="Positif untuk stok masuk, negatif untuk stok keluar.",
    )
    movement_type = models.CharField(max_length=10, choices=MovementType.choices)
    reference = models.CharField(max_length=50, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.product} {self.quantity} @ {self.warehouse}"
