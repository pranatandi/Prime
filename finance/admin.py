from django.contrib import admin

from core.admin import TenantScopedAdmin
from .models import (
    Account, BankAccount, Budget, BudgetLine, Invoice, InvoiceItem, JournalEntry,
    JournalEntryLine, Payment, TaxRate,
)


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 1


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class BudgetLineInline(admin.TabularInline):
    model = BudgetLine
    extra = 1


@admin.register(Account)
class AccountAdmin(TenantScopedAdmin):
    list_display = ("code", "name", "type", "parent", "tenant")
    list_filter = ("tenant", "type")
    search_fields = ("code", "name")


@admin.register(TaxRate)
class TaxRateAdmin(TenantScopedAdmin):
    list_display = ("name", "rate", "tenant")
    list_filter = ("tenant",)


@admin.register(JournalEntry)
class JournalEntryAdmin(TenantScopedAdmin):
    list_display = ("date", "memo", "total_debit", "total_credit", "tenant")
    list_filter = ("tenant",)
    inlines = [JournalEntryLineInline]


@admin.register(Invoice)
class InvoiceAdmin(TenantScopedAdmin):
    list_display = ("number", "customer", "issue_date", "due_date", "status", "total", "tenant")
    list_filter = ("tenant", "status")
    search_fields = ("number",)
    inlines = [InvoiceItemInline]


@admin.register(Budget)
class BudgetAdmin(TenantScopedAdmin):
    list_display = ("name", "fiscal_year", "period", "total_planned", "tenant")
    list_filter = ("tenant", "period")
    inlines = [BudgetLineInline]


@admin.register(BankAccount)
class BankAccountAdmin(TenantScopedAdmin):
    list_display = ("name", "bank_name", "account_number", "is_cash", "book_balance", "tenant")
    list_filter = ("tenant", "is_cash")


@admin.register(Payment)
class PaymentAdmin(TenantScopedAdmin):
    list_display = ("date", "bank_account", "direction", "amount", "contra_account", "invoice", "bill", "is_reconciled", "tenant")
    list_filter = ("tenant", "direction", "is_reconciled")
