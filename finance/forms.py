from django.forms import inlineformset_factory

from core.forms import BootstrapModelForm
from .models import (
    Account, Budget, BudgetLine, Invoice, InvoiceItem, JournalEntry, JournalEntryLine, TaxRate,
)


class AccountForm(BootstrapModelForm):
    class Meta:
        model = Account
        fields = ["code", "name", "type", "parent"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].queryset = Account.objects.filter(tenant=self.tenant)


class TaxRateForm(BootstrapModelForm):
    class Meta:
        model = TaxRate
        fields = ["name", "rate"]


class JournalEntryForm(BootstrapModelForm):
    class Meta:
        model = JournalEntry
        fields = ["date", "memo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs["type"] = "date"


class JournalEntryLineForm(BootstrapModelForm):
    class Meta:
        model = JournalEntryLine
        fields = ["account", "debit", "credit", "description"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
        if tenant:
            self.fields["account"].queryset = Account.objects.filter(tenant=tenant)


JournalEntryLineFormSet = inlineformset_factory(
    JournalEntry, JournalEntryLine, form=JournalEntryLineForm, extra=2, can_delete=True,
)


class InvoiceForm(BootstrapModelForm):
    class Meta:
        model = Invoice
        fields = ["number", "customer", "issue_date", "due_date", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from crm.models import Company
        self.fields["customer"].queryset = Company.objects.filter(tenant=self.tenant)
        self.fields["issue_date"].widget.attrs["type"] = "date"
        self.fields["due_date"].widget.attrs["type"] = "date"


class InvoiceItemForm(BootstrapModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["description", "quantity", "unit_price", "tax_rate"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
        if tenant:
            self.fields["tax_rate"].queryset = TaxRate.objects.filter(tenant=tenant)


InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem, form=InvoiceItemForm, extra=3, can_delete=True,
)


class BudgetForm(BootstrapModelForm):
    class Meta:
        model = Budget
        fields = ["name", "fiscal_year", "period"]


class BudgetLineForm(BootstrapModelForm):
    class Meta:
        model = BudgetLine
        fields = ["account", "planned_amount", "period_start", "period_end"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
        if tenant:
            self.fields["account"].queryset = Account.objects.filter(tenant=tenant)
        self.fields["period_start"].widget.attrs["type"] = "date"
        self.fields["period_end"].widget.attrs["type"] = "date"


BudgetLineFormSet = inlineformset_factory(
    Budget, BudgetLine, form=BudgetLineForm, extra=2, can_delete=True,
)
