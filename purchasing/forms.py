from django.forms import inlineformset_factory

from core.forms import BootstrapModelForm
from .models import PurchaseOrder, PurchaseOrderItem, Vendor


class VendorForm(BootstrapModelForm):
    class Meta:
        model = Vendor
        fields = ["name", "contact_person", "email", "phone", "address"]


class PurchaseOrderForm(BootstrapModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["po_number", "vendor", "order_date", "expected_delivery", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vendor"].queryset = Vendor.objects.filter(tenant=self.tenant)
        self.fields["order_date"].widget.attrs["type"] = "date"
        self.fields["expected_delivery"].widget.attrs["type"] = "date"


class PurchaseOrderItemForm(BootstrapModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ["description", "quantity", "unit_price"]


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemForm, extra=3, can_delete=True,
)
