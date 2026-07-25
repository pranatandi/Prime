from django.contrib import admin

from core.admin import TenantScopedAdmin
from .models import DepreciationEntry, FixedAsset


class DepreciationEntryInline(admin.TabularInline):
    model = DepreciationEntry
    extra = 0


@admin.register(FixedAsset)
class FixedAssetAdmin(TenantScopedAdmin):
    list_display = ("asset_number", "name", "acquisition_cost", "book_value", "status", "tenant")
    list_filter = ("tenant", "status")
    search_fields = ("asset_number", "name")
    inlines = [DepreciationEntryInline]
