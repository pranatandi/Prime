from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
    TenantCSVExportView,
    TenantFormsetMixin,
)
from .forms import (
    AccountForm, BudgetForm, BudgetLineFormSet, InvoiceForm, InvoiceItemFormSet,
    JournalEntryForm, JournalEntryLineFormSet, TaxRateForm,
)
from .models import Account, Budget, Invoice, JournalEntry, TaxRate


# ---- Chart of Accounts ----

class AccountListView(GenericTenantListView):
    model = Account
    title = "Chart of Accounts"
    url_basename = "finance:account"
    list_fields = [("Kode", "code"), ("Nama", "name"), ("Tipe", "get_type_display"), ("Parent", "parent")]


class AccountCreateView(GenericTenantCreateView):
    model = Account
    form_class = AccountForm
    title = "Account"
    url_basename = "finance:account"


class AccountUpdateView(GenericTenantUpdateView):
    model = Account
    form_class = AccountForm
    title = "Account"
    url_basename = "finance:account"


class AccountDeleteView(GenericTenantDeleteView):
    model = Account
    title = "Account"
    url_basename = "finance:account"


# ---- Tax Rates ----

class TaxRateListView(GenericTenantListView):
    model = TaxRate
    title = "Tax Rates"
    url_basename = "finance:taxrate"
    list_fields = [("Nama", "name"), ("Rate (%)", "rate")]


class TaxRateCreateView(GenericTenantCreateView):
    model = TaxRate
    form_class = TaxRateForm
    title = "Tax Rate"
    url_basename = "finance:taxrate"


class TaxRateUpdateView(GenericTenantUpdateView):
    model = TaxRate
    form_class = TaxRateForm
    title = "Tax Rate"
    url_basename = "finance:taxrate"


class TaxRateDeleteView(GenericTenantDeleteView):
    model = TaxRate
    title = "Tax Rate"
    url_basename = "finance:taxrate"


# ---- Journal Entries ----

class JournalEntryListView(GenericTenantListView):
    model = JournalEntry
    title = "Journal Entries"
    url_basename = "finance:journalentry"
    list_fields = [
        ("Tanggal", "date"), ("Memo", "memo"),
        ("Total Debit", "total_debit"), ("Total Kredit", "total_credit"),
    ]


class JournalEntryCreateView(TenantFormsetMixin, GenericTenantCreateView):
    model = JournalEntry
    form_class = JournalEntryForm
    formset_class = JournalEntryLineFormSet
    title = "Journal Entry"
    url_basename = "finance:journalentry"
    template_name = "finance/journalentry_form.html"


class JournalEntryUpdateView(TenantFormsetMixin, GenericTenantUpdateView):
    model = JournalEntry
    form_class = JournalEntryForm
    formset_class = JournalEntryLineFormSet
    title = "Journal Entry"
    url_basename = "finance:journalentry"
    template_name = "finance/journalentry_form.html"


class JournalEntryDeleteView(GenericTenantDeleteView):
    model = JournalEntry
    title = "Journal Entry"
    url_basename = "finance:journalentry"


# ---- Invoices ----

class InvoiceListView(GenericTenantListView):
    model = Invoice
    title = "Invoices"
    url_basename = "finance:invoice"
    has_export = True
    list_fields = [
        ("No.", "number"), ("Customer", "customer"), ("Jatuh Tempo", "due_date"),
        ("Status", "get_status_display"), ("Total", "total"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("customer")


class InvoiceCreateView(TenantFormsetMixin, GenericTenantCreateView):
    model = Invoice
    form_class = InvoiceForm
    formset_class = InvoiceItemFormSet
    title = "Invoice"
    url_basename = "finance:invoice"
    template_name = "finance/invoice_form.html"


class InvoiceUpdateView(TenantFormsetMixin, GenericTenantUpdateView):
    model = Invoice
    form_class = InvoiceForm
    formset_class = InvoiceItemFormSet
    title = "Invoice"
    url_basename = "finance:invoice"
    template_name = "finance/invoice_form.html"


class InvoiceDeleteView(GenericTenantDeleteView):
    model = Invoice
    title = "Invoice"
    url_basename = "finance:invoice"


# ---- Budgets ----

class BudgetListView(GenericTenantListView):
    model = Budget
    title = "Budgets"
    url_basename = "finance:budget"
    list_fields = [
        ("Nama", "name"), ("Tahun", "fiscal_year"),
        ("Periode", "get_period_display"), ("Total Rencana", "total_planned"),
    ]


class BudgetCreateView(TenantFormsetMixin, GenericTenantCreateView):
    model = Budget
    form_class = BudgetForm
    formset_class = BudgetLineFormSet
    title = "Budget"
    url_basename = "finance:budget"
    template_name = "finance/budget_form.html"


class BudgetUpdateView(TenantFormsetMixin, GenericTenantUpdateView):
    model = Budget
    form_class = BudgetForm
    formset_class = BudgetLineFormSet
    title = "Budget"
    url_basename = "finance:budget"
    template_name = "finance/budget_form.html"


class BudgetDeleteView(GenericTenantDeleteView):
    model = Budget
    title = "Budget"
    url_basename = "finance:budget"


# ---- CSV Export ----

class InvoiceExportView(TenantCSVExportView):
    model = Invoice
    filename = "invoices"
    export_fields = [
        ("No.", "number"), ("Customer", "customer"), ("Tgl Terbit", "issue_date"),
        ("Jatuh Tempo", "due_date"), ("Status", "get_status_display"),
        ("Subtotal", "subtotal"), ("Pajak", "tax_total"), ("Total", "total"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("customer")
