from core.forms import BootstrapModelForm
from .models import Product, Warehouse


class WarehouseForm(BootstrapModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "address", "is_default"]


class ProductForm(BootstrapModelForm):
    class Meta:
        model = Product
        fields = [
            "sku", "name", "unit", "cost_price", "sell_price", "track_inventory",
            "inventory_account", "cogs_account", "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from finance.models import Account
        self.fields["inventory_account"].queryset = Account.objects.filter(
            tenant=self.tenant, type=Account.AccountType.ASSET,
        )
        self.fields["cogs_account"].queryset = Account.objects.filter(
            tenant=self.tenant, type=Account.AccountType.EXPENSE,
        )
