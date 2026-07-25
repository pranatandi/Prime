from django.contrib import admin

from core.admin import TenantScopedAdmin
from .models import PurchaseOrder, PurchaseOrderItem, Vendor


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(Vendor)
class VendorAdmin(TenantScopedAdmin):
    list_display = ("name", "contact_person", "email", "phone", "tenant")
    list_filter = ("tenant",)
    search_fields = ("name",)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(TenantScopedAdmin):
    list_display = ("po_number", "vendor", "order_date", "status", "total", "tenant")
    list_filter = ("tenant", "status")
    search_fields = ("po_number",)
    inlines = [PurchaseOrderItemInline]
