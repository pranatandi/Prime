from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import TemplateView

from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
    TenantCSVExportView,
    TenantFormsetMixin,
)
from .forms import (
    AccountForm, BankAccountForm, BudgetForm, BudgetLineFormSet, InvoiceForm, InvoiceItemFormSet,
    JournalEntryForm, JournalEntryLineFormSet, PaymentForm, TaxRateForm,
)
from .models import Account, BankAccount, Budget, Invoice, JournalEntry, JournalEntryLine, Payment, TaxRate


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
        ("Status", "get_status_display"), ("Total", "total"), ("Sisa Tagihan", "balance_due"),
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


# ---- Bank & Kas ----

class BankAccountListView(GenericTenantListView):
    model = BankAccount
    title = "Bank Accounts"
    url_basename = "finance:bankaccount"
    template_name = "finance/bankaccount_list.html"
    list_fields = [
        ("Nama", "name"), ("Bank", "bank_name"), ("No. Rekening", "account_number"),
        ("Kas?", "is_cash"), ("Saldo Buku", "book_balance"),
    ]


class BankAccountCreateView(GenericTenantCreateView):
    model = BankAccount
    form_class = BankAccountForm
    title = "Bank Account"
    url_basename = "finance:bankaccount"


class BankAccountUpdateView(GenericTenantUpdateView):
    model = BankAccount
    form_class = BankAccountForm
    title = "Bank Account"
    url_basename = "finance:bankaccount"


class BankAccountDeleteView(GenericTenantDeleteView):
    model = BankAccount
    title = "Bank Account"
    url_basename = "finance:bankaccount"


class BankReconciliationView(LoginRequiredMixin, TemplateView):
    template_name = "finance/reconciliation.html"

    def get_bank_account(self):
        return get_object_or_404(BankAccount, pk=self.kwargs["pk"], tenant=self.request.user.tenant)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bank_account = self.get_bank_account()
        ctx["bank_account"] = bank_account
        ctx["payments"] = bank_account.payments.select_related("contra_account", "invoice").order_by("-date")
        ctx["difference"] = bank_account.book_balance - bank_account.reconciled_balance
        return ctx

    def post(self, request, *args, **kwargs):
        bank_account = self.get_bank_account()
        reconciled_ids = set(request.POST.getlist("reconciled"))
        now = timezone.now()
        for payment in bank_account.payments.all():
            should_be_reconciled = str(payment.pk) in reconciled_ids
            if should_be_reconciled != payment.is_reconciled:
                payment.is_reconciled = should_be_reconciled
                payment.reconciled_at = now if should_be_reconciled else None
                payment.save(update_fields=["is_reconciled", "reconciled_at"])
        messages.success(request, "Rekonsiliasi berhasil disimpan.")
        return redirect("finance:bankaccount_reconcile", pk=bank_account.pk)


class PaymentListView(GenericTenantListView):
    model = Payment
    title = "Payments"
    url_basename = "finance:payment"
    list_fields = [
        ("Tanggal", "date"), ("Bank/Kas", "bank_account"), ("Arah", "get_direction_display"),
        ("Jumlah", "amount"), ("Akun Lawan", "contra_account"), ("Invoice", "invoice"), ("Reconciled?", "is_reconciled"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("bank_account", "contra_account", "invoice")


class PaymentCreateView(GenericTenantCreateView):
    model = Payment
    form_class = PaymentForm
    title = "Payment"
    url_basename = "finance:payment"


class PaymentDeleteView(GenericTenantDeleteView):
    model = Payment
    title = "Payment"
    url_basename = "finance:payment"

    def form_valid(self, form):
        payment = self.object
        journal_entry = payment.journal_entry
        response = super().form_valid(form)
        if journal_entry:
            journal_entry.delete()
        return response


# ---- Laporan Keuangan ----

def _account_balances(tenant, account_type, debit_normal, **date_filters):
    """Sum JournalEntryLine debit/credit per Account of the given type within
    an optional date window, returning [(account, balance), ...] and the total.
    Zero-balance accounts are omitted.
    """
    rows = (
        JournalEntryLine.objects.filter(entry__tenant=tenant, account__type=account_type, **date_filters)
        .values("account", "account__code", "account__name")
        .annotate(debit_total=Sum("debit"), credit_total=Sum("credit"))
        .order_by("account__code")
    )
    result = []
    total = Decimal("0")
    for row in rows:
        debit = row["debit_total"] or Decimal("0")
        credit = row["credit_total"] or Decimal("0")
        balance = (debit - credit) if debit_normal else (credit - debit)
        if balance != 0:
            result.append({"code": row["account__code"], "name": row["account__name"], "balance": balance})
            total += balance
    return result, total


class BalanceSheetView(LoginRequiredMixin, TemplateView):
    template_name = "finance/balance_sheet.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        as_of = self.request.GET.get("as_of") or timezone.localdate().isoformat()
        window = {"entry__date__lte": as_of}

        assets, total_assets = _account_balances(tenant, Account.AccountType.ASSET, True, **window)
        liabilities, total_liabilities = _account_balances(tenant, Account.AccountType.LIABILITY, False, **window)
        equity, total_equity = _account_balances(tenant, Account.AccountType.EQUITY, False, **window)
        _, total_income = _account_balances(tenant, Account.AccountType.INCOME, False, **window)
        _, total_expense = _account_balances(tenant, Account.AccountType.EXPENSE, True, **window)

        current_earnings = total_income - total_expense
        total_equity_with_earnings = total_equity + current_earnings

        ctx.update({
            "as_of": as_of,
            "assets": assets, "total_assets": total_assets,
            "liabilities": liabilities, "total_liabilities": total_liabilities,
            "equity": equity, "total_equity": total_equity,
            "current_earnings": current_earnings,
            "total_equity_with_earnings": total_equity_with_earnings,
            "total_liabilities_equity": total_liabilities + total_equity_with_earnings,
        })
        return ctx


class IncomeStatementView(LoginRequiredMixin, TemplateView):
    template_name = "finance/income_statement.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        today = timezone.localdate()
        start = self.request.GET.get("start") or today.replace(day=1).isoformat()
        end = self.request.GET.get("end") or today.isoformat()
        window = {"entry__date__gte": start, "entry__date__lte": end}

        income, total_income = _account_balances(tenant, Account.AccountType.INCOME, False, **window)
        expense, total_expense = _account_balances(tenant, Account.AccountType.EXPENSE, True, **window)

        ctx.update({
            "start": start, "end": end,
            "income": income, "total_income": total_income,
            "expense": expense, "total_expense": total_expense,
            "net_income": total_income - total_expense,
        })
        return ctx


class CashFlowView(LoginRequiredMixin, TemplateView):
    template_name = "finance/cash_flow.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        today = timezone.localdate()
        start = self.request.GET.get("start") or today.replace(day=1).isoformat()
        end = self.request.GET.get("end") or today.isoformat()

        rows = []
        total_in = total_out = Decimal("0")
        for bank_account in BankAccount.objects.filter(tenant=tenant):
            payments_before = bank_account.payments.filter(date__lt=start)
            beginning = bank_account.opening_balance
            beginning += sum((p.amount for p in payments_before if p.direction == Payment.Direction.IN), Decimal("0"))
            beginning -= sum((p.amount for p in payments_before if p.direction == Payment.Direction.OUT), Decimal("0"))

            period_payments = bank_account.payments.filter(date__gte=start, date__lte=end)
            cash_in = sum((p.amount for p in period_payments if p.direction == Payment.Direction.IN), Decimal("0"))
            cash_out = sum((p.amount for p in period_payments if p.direction == Payment.Direction.OUT), Decimal("0"))
            ending = beginning + cash_in - cash_out

            rows.append({
                "bank_account": bank_account, "beginning": beginning,
                "cash_in": cash_in, "cash_out": cash_out, "ending": ending,
            })
            total_in += cash_in
            total_out += cash_out

        ctx.update({
            "start": start, "end": end, "rows": rows,
            "total_in": total_in, "total_out": total_out, "net_change": total_in - total_out,
        })
        return ctx
