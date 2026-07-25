from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView

from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
    TenantCSVExportView,
)
from finance.models import JournalEntry, JournalEntryLine
from .forms import FixedAssetForm
from .models import DepreciationEntry, FixedAsset


def _current_period():
    return timezone.localdate().replace(day=1)


def _post_depreciation(asset, period):
    """Posts one month of straight-line depreciation for `asset` at `period`
    (first-of-month date). Returns the created DepreciationEntry, or None if
    nothing was posted (already posted this period, inactive, or fully
    depreciated).
    """
    if asset.status != FixedAsset.Status.ACTIVE:
        return None
    if DepreciationEntry.objects.filter(fixed_asset=asset, period=period).exists():
        return None

    remaining = asset.book_value - asset.salvage_value
    if remaining <= 0:
        asset.status = FixedAsset.Status.FULLY_DEPRECIATED
        asset.save(update_fields=["status"])
        return None

    amount = min(asset.monthly_depreciation, remaining)
    if amount <= 0:
        return None

    entry = JournalEntry.objects.create(
        tenant=asset.tenant, date=period, memo=f"Penyusutan {asset.asset_number} - {period:%B %Y}",
    )
    JournalEntryLine.objects.create(entry=entry, account=asset.depreciation_expense_account, debit=amount)
    JournalEntryLine.objects.create(entry=entry, account=asset.accumulated_depreciation_account, credit=amount)
    dep_entry = DepreciationEntry.objects.create(fixed_asset=asset, period=period, amount=amount, journal_entry=entry)

    if asset.book_value - asset.salvage_value <= 0:
        asset.status = FixedAsset.Status.FULLY_DEPRECIATED
        asset.save(update_fields=["status"])

    return dep_entry


class FixedAssetListView(GenericTenantListView):
    model = FixedAsset
    title = "Fixed Assets"
    url_basename = "assets:fixedasset"
    has_export = True
    template_name = "assets/fixedasset_list.html"
    list_fields = [
        ("No. Aset", "asset_number"), ("Nama", "name"), ("Tgl Perolehan", "acquisition_date"),
        ("Harga Perolehan", "acquisition_cost"), ("Nilai Buku", "book_value"), ("Status", "get_status_display"),
    ]


class FixedAssetCreateView(GenericTenantCreateView):
    model = FixedAsset
    form_class = FixedAssetForm
    title = "Fixed Asset"
    url_basename = "assets:fixedasset"


class FixedAssetUpdateView(GenericTenantUpdateView):
    model = FixedAsset
    form_class = FixedAssetForm
    title = "Fixed Asset"
    url_basename = "assets:fixedasset"


class FixedAssetDeleteView(GenericTenantDeleteView):
    model = FixedAsset
    title = "Fixed Asset"
    url_basename = "assets:fixedasset"


class FixedAssetDetailView(LoginRequiredMixin, DetailView):
    model = FixedAsset
    template_name = "assets/fixedasset_detail.html"
    context_object_name = "asset"

    def get_queryset(self):
        return FixedAsset.objects.filter(tenant=self.request.user.tenant).prefetch_related("depreciation_entries")


class FixedAssetPostDepreciationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(FixedAsset, pk=pk, tenant=request.user.tenant)
        entry = _post_depreciation(asset, _current_period())
        if entry:
            messages.success(request, f"Penyusutan berhasil diposting: Rp {entry.amount:,.0f}".replace(",", "."))
        else:
            messages.warning(
                request,
                "Tidak ada penyusutan yang diposting (sudah diposting bulan ini, aset sudah fully depreciated, atau non-aktif).",
            )
        return redirect("assets:fixedasset_detail", pk=asset.pk)


class FixedAssetDisposeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(FixedAsset, pk=pk, tenant=request.user.tenant)
        asset.status = FixedAsset.Status.DISPOSED
        asset.disposal_date = timezone.localdate()
        asset.save(update_fields=["status", "disposal_date"])
        messages.success(request, "Aset ditandai sebagai disposed.")
        return redirect("assets:fixedasset_detail", pk=asset.pk)


class FixedAssetRunDepreciationAllView(LoginRequiredMixin, View):
    def post(self, request):
        period = _current_period()
        count = 0
        for asset in FixedAsset.objects.filter(tenant=request.user.tenant, status=FixedAsset.Status.ACTIVE):
            if _post_depreciation(asset, period):
                count += 1
        messages.success(request, f"Penyusutan diposting untuk {count} aset.")
        return redirect("assets:fixedasset_list")


class FixedAssetExportView(TenantCSVExportView):
    model = FixedAsset
    filename = "fixed_assets"
    export_fields = [
        ("No. Aset", "asset_number"), ("Nama", "name"), ("Kategori", "category"),
        ("Tgl Perolehan", "acquisition_date"), ("Harga Perolehan", "acquisition_cost"),
        ("Akumulasi Penyusutan", "accumulated_depreciation"), ("Nilai Buku", "book_value"),
        ("Status", "get_status_display"),
    ]
