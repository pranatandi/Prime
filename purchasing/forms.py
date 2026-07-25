from django import forms
from django.forms import inlineformset_factory

from core.forms import BootstrapModelForm
from finance.models import Account, TaxRate
from inventory.models import Product, Warehouse
from .models import Bill, BillItem, PurchaseOrder, PurchaseOrderItem, Vendor


class VendorForm(BootstrapModelForm):
    class Meta:
        model = Vendor
        fields = ["name", "contact_person", "email", "phone", "address"]


class PurchaseOrderForm(BootstrapModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["po_number", "vendor", "warehouse", "order_date", "expected_delivery", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vendor"].queryset = Vendor.objects.filter(tenant=self.tenant)
        self.fields["warehouse"].queryset = Warehouse.objects.filter(tenant=self.tenant)
        self.fields["warehouse"].required = False
        self.fields["order_date"].widget.attrs["type"] = "date"
        self.fields["expected_delivery"].widget.attrs["type"] = "date"


class PurchaseOrderItemForm(BootstrapModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ["product", "description", "quantity", "unit_price"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
        if tenant:
            self.fields["product"].queryset = Product.objects.filter(tenant=tenant)


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemForm, extra=3, can_delete=True,
)


class PurchaseOrderReceiveForm(forms.Form):
    contra_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        help_text="Akun lawan atas penerimaan barang ini, mis. Hutang Usaha / Hutang Barang Belum Ditagih.",
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-select" if isinstance(field.widget, forms.Select) else "form-control")
        if tenant:
            self.fields["contra_account"].queryset = Account.objects.filter(tenant=tenant)


class BillForm(BootstrapModelForm):
    class Meta:
        model = Bill
        fields = ["number", "vendor", "purchase_order", "bill_date", "due_date", "status", "currency", "exchange_rate"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vendor"].queryset = Vendor.objects.filter(tenant=self.tenant)
        self.fields["purchase_order"].queryset = PurchaseOrder.objects.filter(tenant=self.tenant)
        self.fields["purchase_order"].required = False
        self.fields["bill_date"].widget.attrs["type"] = "date"
        self.fields["due_date"].widget.attrs["type"] = "date"


class BillItemForm(BootstrapModelForm):
    class Meta:
        model = BillItem
        fields = ["description", "quantity", "unit_price", "tax_rate"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
        if tenant:
            self.fields["tax_rate"].queryset = TaxRate.objects.filter(tenant=tenant)


BillItemFormSet = inlineformset_factory(
    Bill, BillItem, form=BillItemForm, extra=3, can_delete=True,
)
