from core.forms import BootstrapModelForm
from finance.models import Account
from .models import FixedAsset


class FixedAssetForm(BootstrapModelForm):
    class Meta:
        model = FixedAsset
        fields = [
            "asset_number", "name", "category", "acquisition_date", "acquisition_cost", "salvage_value",
            "useful_life_months", "asset_account", "accumulated_depreciation_account", "depreciation_expense_account",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acquisition_date"].widget.attrs["type"] = "date"
        self.fields["asset_account"].queryset = Account.objects.filter(
            tenant=self.tenant, type=Account.AccountType.ASSET,
        )
        self.fields["accumulated_depreciation_account"].queryset = Account.objects.filter(
            tenant=self.tenant, type=Account.AccountType.ASSET,
        )
        self.fields["depreciation_expense_account"].queryset = Account.objects.filter(
            tenant=self.tenant, type=Account.AccountType.EXPENSE,
        )
