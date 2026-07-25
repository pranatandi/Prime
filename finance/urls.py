from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    # Chart of accounts
    path("accounts/", views.AccountListView.as_view(), name="account_list"),
    path("accounts/add/", views.AccountCreateView.as_view(), name="account_create"),
    path("accounts/<int:pk>/edit/", views.AccountUpdateView.as_view(), name="account_edit"),
    path("accounts/<int:pk>/delete/", views.AccountDeleteView.as_view(), name="account_delete"),
    # Tax rates
    path("tax-rates/", views.TaxRateListView.as_view(), name="taxrate_list"),
    path("tax-rates/add/", views.TaxRateCreateView.as_view(), name="taxrate_create"),
    path("tax-rates/<int:pk>/edit/", views.TaxRateUpdateView.as_view(), name="taxrate_edit"),
    path("tax-rates/<int:pk>/delete/", views.TaxRateDeleteView.as_view(), name="taxrate_delete"),
    # Journal entries
    path("journal-entries/", views.JournalEntryListView.as_view(), name="journalentry_list"),
    path("journal-entries/add/", views.JournalEntryCreateView.as_view(), name="journalentry_create"),
    path("journal-entries/<int:pk>/edit/", views.JournalEntryUpdateView.as_view(), name="journalentry_edit"),
    path("journal-entries/<int:pk>/delete/", views.JournalEntryDeleteView.as_view(), name="journalentry_delete"),
    # Invoices
    path("invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("invoices/add/", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoices/export/", views.InvoiceExportView.as_view(), name="invoice_export"),
    path("invoices/<int:pk>/edit/", views.InvoiceUpdateView.as_view(), name="invoice_edit"),
    path("invoices/<int:pk>/delete/", views.InvoiceDeleteView.as_view(), name="invoice_delete"),
    # Budgets
    path("budgets/", views.BudgetListView.as_view(), name="budget_list"),
    path("budgets/add/", views.BudgetCreateView.as_view(), name="budget_create"),
    path("budgets/<int:pk>/edit/", views.BudgetUpdateView.as_view(), name="budget_edit"),
    path("budgets/<int:pk>/delete/", views.BudgetDeleteView.as_view(), name="budget_delete"),
    # Bank accounts
    path("bank-accounts/", views.BankAccountListView.as_view(), name="bankaccount_list"),
    path("bank-accounts/add/", views.BankAccountCreateView.as_view(), name="bankaccount_create"),
    path("bank-accounts/<int:pk>/edit/", views.BankAccountUpdateView.as_view(), name="bankaccount_edit"),
    path("bank-accounts/<int:pk>/delete/", views.BankAccountDeleteView.as_view(), name="bankaccount_delete"),
    path("bank-accounts/<int:pk>/reconcile/", views.BankReconciliationView.as_view(), name="bankaccount_reconcile"),
    # Payments
    path("payments/", views.PaymentListView.as_view(), name="payment_list"),
    path("payments/add/", views.PaymentCreateView.as_view(), name="payment_create"),
    path("payments/<int:pk>/delete/", views.PaymentDeleteView.as_view(), name="payment_delete"),
    # Laporan keuangan
    path("reports/balance-sheet/", views.BalanceSheetView.as_view(), name="balance_sheet"),
    path("reports/income-statement/", views.IncomeStatementView.as_view(), name="income_statement"),
    path("reports/cash-flow/", views.CashFlowView.as_view(), name="cash_flow"),
]
