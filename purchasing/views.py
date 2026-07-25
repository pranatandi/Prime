from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
    TenantFormsetMixin,
)
from .forms import PurchaseOrderForm, PurchaseOrderItemFormSet, VendorForm
from .models import PurchaseOrder, Vendor


# ---- Vendors ----

class VendorListView(GenericTenantListView):
    model = Vendor
    title = "Vendors"
    url_basename = "purchasing:vendor"
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
    list_fields = [
        ("No. PO", "po_number"), ("Vendor", "vendor"), ("Tgl Order", "order_date"),
        ("Status", "get_status_display"), ("Total", "total"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("vendor")


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
