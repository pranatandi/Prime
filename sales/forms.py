from django.forms import inlineformset_factory

from core.forms import BootstrapModelForm
from crm.models import Company
from finance.models import TaxRate
from inventory.models import Product, Warehouse
from .models import SalesOrder, SalesOrderItem


class SalesOrderForm(BootstrapModelForm):
    class Meta:
        model = SalesOrder
        fields = ["so_number", "customer", "warehouse", "order_date", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Company.objects.filter(tenant=self.tenant)
        self.fields["warehouse"].queryset = Warehouse.objects.filter(tenant=self.tenant)
        self.fields["order_date"].widget.attrs["type"] = "date"


class SalesOrderItemForm(BootstrapModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ["product", "description", "quantity", "unit_price", "tax_rate"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
        if tenant:
            self.fields["product"].queryset = Product.objects.filter(tenant=tenant)
            self.fields["tax_rate"].queryset = TaxRate.objects.filter(tenant=tenant)


SalesOrderItemFormSet = inlineformset_factory(
    SalesOrder, SalesOrderItem, form=SalesOrderItemForm, extra=3, can_delete=True,
)
