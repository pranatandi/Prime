from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from core.signals import connect_audit_log
        from crm.models import Activity, Company, Contact, Deal
        from finance.models import Account, BankAccount, Budget, Invoice, JournalEntry, Payment
        from inventory.models import Product
        from payroll.models import Employee, PayrollRun
        from purchasing.models import Bill, PurchaseOrder, Vendor
        from sales.models import SalesOrder

        connect_audit_log([
            Company, Contact, Deal, Activity,
            Account, JournalEntry, Invoice, Budget, BankAccount, Payment,
            Employee, PayrollRun,
            Vendor, PurchaseOrder, Bill,
            Product, SalesOrder,
        ])
