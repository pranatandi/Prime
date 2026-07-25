from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView

from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
    TenantCSVExportView,
    TenantFormsetMixin,
)
from finance.models import JournalEntry, JournalEntryLine
from inventory.models import StockMovement
from .forms import (
    BillForm, BillItemFormSet, PurchaseOrderForm, PurchaseOrderItemFormSet,
    PurchaseOrderReceiveForm, VendorForm,
)
from .models import Bill, PurchaseOrder, Vendor


# ---- Vendors ----

class VendorListView(GenericTenantListView):
    model = Vendor
    title = "Vendors"
    url_basename = "purchasing:vendor"
    has_export = True
    list_fields = [("Nama", "name"), ("Kontak", "contact_person"), ("Email", "email"), ("Telepon", "phone")]


class VendorCreateView(GenericTenantCreateView):
    model = Vendor
    form_class = VendorForm
    title = "Vendor"
    url_basename = "purchasing:vendor"


class VendorUpdateView(GenericTenantUpdateView):
    model = Vendor
    form_class = VendorForm
    title = "Vendor"
    url_basename = "purchasing:vendor"


class VendorDeleteView(GenericTenantDeleteView):
    model = Vendor
    title = "Vendor"
    url_basename = "purchasing:vendor"


# ---- Purchase Orders ----

class PurchaseOrderListView(GenericTenantListView):
    model = PurchaseOrder
    title = "Purchase Orders"
    url_basename = "purchasing:purchaseorder"
    has_export = True
    template_name = "purchasing/purchaseorder_list.html"

    def get_queryset(self):
        return super().get_queryset().select_related("vendor")


class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = "purchasing/purchaseorder_detail.html"
    context_object_name = "po"

    def get_queryset(self):
        return PurchaseOrder.objects.filter(tenant=self.request.user.tenant).select_related("vendor", "warehouse")


class PurchaseOrderCreateView(TenantFormsetMixin, GenericTenantCreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    formset_class = PurchaseOrderItemFormSet
    title = "Purchase Order"
    url_basename = "purchasing:purchaseorder"
    template_name = "purchasing/purchaseorder_form.html"


class PurchaseOrderUpdateView(TenantFormsetMixin, GenericTenantUpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    formset_class = PurchaseOrderItemFormSet
    title = "Purchase Order"
    url_basename = "purchasing:purchaseorder"
    template_name = "purchasing/purchaseorder_form.html"


class PurchaseOrderDeleteView(GenericTenantDeleteView):
    model = PurchaseOrder
    title = "Purchase Order"
    url_basename = "purchasing:purchaseorder"


class PurchaseOrderReceiveView(LoginRequiredMixin, View):
    """Marks a Purchase Order as received: adds stock and posts a journal
    entry (Debit Inventory / Credit the chosen contra account) for products
    that have an inventory account configured.
    """

    def _get_po(self, request, pk):
        return get_object_or_404(PurchaseOrder, pk=pk, tenant=request.user.tenant)

    def get(self, request, pk):
        po = self._get_po(request, pk)
        form = PurchaseOrderReceiveForm(tenant=request.user.tenant)
        return render(request, "purchasing/purchaseorder_receive.html", {"po": po, "form": form})

    def post(self, request, pk):
        po = self._get_po(request, pk)
        if po.status not in (PurchaseOrder.Status.DRAFT, PurchaseOrder.Status.SENT):
            messages.error(request, "Purchase Order ini sudah diterima atau dibatalkan.")
            return redirect("purchasing:purchaseorder_detail", pk=po.pk)
        if not po.warehouse_id:
            messages.error(request, "Pilih Warehouse di Purchase Order sebelum menandai diterima.")
            return redirect("purchasing:purchaseorder_detail", pk=po.pk)

        form = PurchaseOrderReceiveForm(request.POST, tenant=request.user.tenant)
        if not form.is_valid():
            return render(request, "purchasing/purchaseorder_receive.html", {"po": po, "form": form})
        contra_account = form.cleaned_data["contra_account"]

        today = timezone.localdate()
        entry = None
        for item in po.items.select_related("product"):
            product = item.product
            if not product or not product.track_inventory:
                continue
            StockMovement.objects.create(
                tenant=po.tenant, product=product, warehouse=po.warehouse, date=today,
                quantity=item.quantity, movement_type=StockMovement.MovementType.RECEIPT,
                reference=po.po_number,
            )
            if product.inventory_account_id:
                amount = item.unit_price * item.quantity
                if amount > 0:
                    if entry is None:
                        entry = JournalEntry.objects.create(
                            tenant=po.tenant, date=today, memo=f"Penerimaan Barang {po.po_number}",
                        )
                    JournalEntryLine.objects.create(entry=entry, account=product.inventory_account, debit=amount)
                    JournalEntryLine.objects.create(entry=entry, account=contra_account, credit=amount)

        po.status = PurchaseOrder.Status.RECEIVED
        po.save()
        messages.success(request, "Purchase Order ditandai diterima. Stok & jurnal telah diperbarui.")
        return redirect("purchasing:purchaseorder_detail", pk=po.pk)


class PurchaseOrderCreateBillView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk, tenant=request.user.tenant)
        today = timezone.localdate()
        bill = Bill.objects.create(
            tenant=po.tenant, number=f"BILL-{po.po_number}-{po.bills.count() + 1}", vendor=po.vendor,
            purchase_order=po, bill_date=today, due_date=today + timedelta(days=14), status=Bill.Status.DRAFT,
        )
        for item in po.items.all():
            bill.items.create(description=item.description, quantity=item.quantity, unit_price=item.unit_price)
        messages.success(request, "Bill berhasil dibuat dari Purchase Order.")
        return redirect("purchasing:bill_edit", pk=bill.pk)


# ---- Bills ----

class BillListView(GenericTenantListView):
    model = Bill
    title = "Bills"
    url_basename = "purchasing:bill"
    has_export = True
    list_fields = [
        ("No.", "number"), ("Vendor", "vendor"), ("Jatuh Tempo", "due_date"),
        ("Status", "get_status_display"), ("Total", "total"), ("Sisa Hutang", "balance_due"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("vendor")


class BillCreateView(TenantFormsetMixin, GenericTenantCreateView):
    model = Bill
    form_class = BillForm
    formset_class = BillItemFormSet
    title = "Bill"
    url_basename = "purchasing:bill"
    template_name = "purchasing/bill_form.html"


class BillUpdateView(TenantFormsetMixin, GenericTenantUpdateView):
    model = Bill
    form_class = BillForm
    formset_class = BillItemFormSet
    title = "Bill"
    url_basename = "purchasing:bill"
    template_name = "purchasing/bill_form.html"


class BillDeleteView(GenericTenantDeleteView):
    model = Bill
    title = "Bill"
    url_basename = "purchasing:bill"


# ---- CSV Export ----

class VendorExportView(TenantCSVExportView):
    model = Vendor
    filename = "vendors"
    export_fields = [("Nama", "name"), ("Kontak", "contact_person"), ("Email", "email"), ("Telepon", "phone")]


class PurchaseOrderExportView(TenantCSVExportView):
    model = PurchaseOrder
    filename = "purchase_orders"
    export_fields = [
        ("No. PO", "po_number"), ("Vendor", "vendor"), ("Tgl Order", "order_date"),
        ("Status", "get_status_display"), ("Total", "total"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("vendor")


class BillExportView(TenantCSVExportView):
    model = Bill
    filename = "bills"
    export_fields = [
        ("No.", "number"), ("Vendor", "vendor"), ("Tgl Bill", "bill_date"), ("Jatuh Tempo", "due_date"),
        ("Status", "get_status_display"), ("Total", "total"), ("Sisa Hutang", "balance_due"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("vendor")
