from django.contrib import admin

from core.admin import TenantScopedAdmin
from .models import SalesOrder, SalesOrderItem


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1


@admin.register(SalesOrder)
class SalesOrderAdmin(TenantScopedAdmin):
    list_display = ("so_number", "customer", "order_date", "status", "total", "tenant")
    list_filter = ("tenant", "status")
    search_fields = ("so_number",)
    inlines = [SalesOrderItemInline]
