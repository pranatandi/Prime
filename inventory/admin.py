from django.contrib import admin

from core.admin import TenantScopedAdmin
from .models import Product, StockMovement, Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(TenantScopedAdmin):
    list_display = ("name", "address", "is_default", "tenant")
    list_filter = ("tenant", "is_default")


@admin.register(Product)
class ProductAdmin(TenantScopedAdmin):
    list_display = ("sku", "name", "unit", "cost_price", "sell_price", "total_stock", "is_active", "tenant")
    list_filter = ("tenant", "is_active", "track_inventory")
    search_fields = ("sku", "name")


@admin.register(StockMovement)
class StockMovementAdmin(TenantScopedAdmin):
    list_display = ("date", "product", "warehouse", "movement_type", "quantity", "reference", "tenant")
    list_filter = ("tenant", "movement_type")
