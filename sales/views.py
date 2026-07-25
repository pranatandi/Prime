from datetime import timedelta

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
    TenantFormsetMixin,
)
from finance.models import Invoice, InvoiceItem, JournalEntry, JournalEntryLine
from inventory.models import StockMovement
from .forms import SalesOrderForm, SalesOrderItemFormSet
from .models import SalesOrder


class SalesOrderListView(GenericTenantListView):
    model = SalesOrder
    title = "Sales Orders"
    url_basename = "sales:salesorder"
    template_name = "sales/salesorder_list.html"

    def get_queryset(self):
        return super().get_queryset().select_related("customer")


class SalesOrderDetailView(LoginRequiredMixin, DetailView):
    model = SalesOrder
    template_name = "sales/salesorder_detail.html"
    context_object_name = "so"

    def get_queryset(self):
        return SalesOrder.objects.filter(tenant=self.request.user.tenant).select_related("customer", "warehouse", "invoice")


class SalesOrderCreateView(TenantFormsetMixin, GenericTenantCreateView):
    model = SalesOrder
    form_class = SalesOrderForm
    formset_class = SalesOrderItemFormSet
    title = "Sales Order"
    url_basename = "sales:salesorder"
    template_name = "sales/salesorder_form.html"


class SalesOrderUpdateView(TenantFormsetMixin, GenericTenantUpdateView):
    model = SalesOrder
    form_class = SalesOrderForm
    formset_class = SalesOrderItemFormSet
    title = "Sales Order"
    url_basename = "sales:salesorder"
    template_name = "sales/salesorder_form.html"


class SalesOrderDeleteView(GenericTenantDeleteView):
    model = SalesOrder
    title = "Sales Order"
    url_basename = "sales:salesorder"


class SalesOrderDeliverView(LoginRequiredMixin, View):
    """Marks a Sales Order as delivered: deducts stock and posts a COGS
    journal entry (Debit COGS / Credit Inventory) for products that have
    both accounts configured.
    """

    def post(self, request, pk):
        so = get_object_or_404(SalesOrder, pk=pk, tenant=request.user.tenant)
        if so.status not in (SalesOrder.Status.DRAFT, SalesOrder.Status.CONFIRMED):
            messages.error(request, "Sales Order ini sudah terkirim, ter-invoice, atau dibatalkan.")
            return redirect("sales:salesorder_detail", pk=so.pk)
        if not so.warehouse_id:
            messages.error(request, "Pilih Warehouse di Sales Order sebelum menandai terkirim.")
            return redirect("sales:salesorder_detail", pk=so.pk)

        today = timezone.localdate()
        for item in so.items.select_related("product"):
            product = item.product
            if not product or not product.track_inventory:
                continue
            StockMovement.objects.create(
                tenant=so.tenant, product=product, warehouse=so.warehouse, date=today,
                quantity=-item.quantity, movement_type=StockMovement.MovementType.DELIVERY,
                reference=so.so_number,
            )
            if product.inventory_account_id and product.cogs_account_id:
                amount = product.cost_price * item.quantity
                if amount > 0:
                    entry = JournalEntry.objects.create(
                        tenant=so.tenant, date=today, memo=f"HPP {so.so_number} - {product.sku}",
                    )
                    JournalEntryLine.objects.create(entry=entry, account=product.cogs_account, debit=amount)
                    JournalEntryLine.objects.create(entry=entry, account=product.inventory_account, credit=amount)

        so.status = SalesOrder.Status.DELIVERED
        so.save()
        messages.success(request, "Sales Order ditandai terkirim. Stok & jurnal HPP telah diperbarui.")
        return redirect("sales:salesorder_detail", pk=so.pk)


class SalesOrderCreateInvoiceView(LoginRequiredMixin, View):
    def post(self, request, pk):
        so = get_object_or_404(SalesOrder, pk=pk, tenant=request.user.tenant)
        if so.invoice_id:
            messages.warning(request, "Sales Order ini sudah punya invoice.")
            return redirect("finance:invoice_edit", pk=so.invoice_id)

        today = timezone.localdate()
        invoice = Invoice.objects.create(
            tenant=so.tenant, number=f"INV-{so.so_number}", customer=so.customer,
            issue_date=today, due_date=today + timedelta(days=14), status=Invoice.Status.DRAFT,
        )
        for item in so.items.all():
            InvoiceItem.objects.create(
                invoice=invoice, description=item.description, quantity=item.quantity,
                unit_price=item.unit_price, tax_rate=item.tax_rate,
            )
        so.invoice = invoice
        so.status = SalesOrder.Status.INVOICED
        so.save()
        messages.success(request, "Invoice berhasil dibuat dari Sales Order.")
        return redirect("finance:invoice_edit", pk=invoice.pk)
