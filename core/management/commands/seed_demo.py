import datetime

from django.core.management.base import BaseCommand

from accounts.models import User
from core.models import Tenant
from crm.models import Activity, Company, Contact, Deal, PipelineStage
from finance.models import Account, Invoice, InvoiceItem, TaxRate
from payroll.models import Employee
from purchasing.models import PurchaseOrder, PurchaseOrderItem, Vendor


class Command(BaseCommand):
    help = "Seed two demo tenants with sample CRM/ERP data (safe to re-run)."

    def handle(self, *args, **options):
        for name, username in [("Acme Corporation", "admin_acme"), ("Nusantara Retail", "admin_nusantara")]:
            self._seed_tenant(name, username)
        self.stdout.write(self.style.SUCCESS("Demo data ready. Login with admin_acme / admin_nusantara, password: demo12345"))

    def _seed_tenant(self, tenant_name, admin_username):
        tenant, _ = Tenant.objects.get_or_create(name=tenant_name)

        admin, created = User.objects.get_or_create(
            username=admin_username,
            defaults={"tenant": tenant, "role": User.Role.ADMIN, "email": f"{admin_username}@example.com"},
        )
        if created:
            admin.set_password("demo12345")
            admin.save()

        stage_names = [("New", False, False), ("Qualified", False, False), ("Proposal", False, False),
                       ("Negotiation", False, False), ("Won", True, False), ("Lost", False, True)]
        stages = {}
        for i, (name, is_won, is_lost) in enumerate(stage_names):
            stage, _ = PipelineStage.objects.get_or_create(
                tenant=tenant, name=name, defaults={"order": i, "is_won": is_won, "is_lost": is_lost},
            )
            stages[name] = stage

        company, _ = Company.objects.get_or_create(
            tenant=tenant, name=f"{tenant_name} Client A",
            defaults={"industry": "Manufacturing", "phone": "021-5550001", "owner": admin},
        )
        contact, _ = Contact.objects.get_or_create(
            tenant=tenant, first_name="Budi", last_name="Santoso",
            defaults={"company": company, "email": "budi@example.com", "owner": admin},
        )
        Deal.objects.get_or_create(
            tenant=tenant, title=f"{company.name} - Implementasi Sistem",
            defaults={"company": company, "contact": contact, "stage": stages["Proposal"], "value": 150_000_000, "owner": admin},
        )
        Activity.objects.get_or_create(
            tenant=tenant, subject="Follow up proposal",
            defaults={"type": Activity.Type.CALL, "contact": contact, "due_date": datetime.date.today(), "assigned_to": admin},
        )

        Account.objects.get_or_create(tenant=tenant, code="1000", defaults={"name": "Kas", "type": Account.AccountType.ASSET})
        Account.objects.get_or_create(tenant=tenant, code="4000", defaults={"name": "Pendapatan Jasa", "type": Account.AccountType.INCOME})
        Account.objects.get_or_create(tenant=tenant, code="5000", defaults={"name": "Beban Operasional", "type": Account.AccountType.EXPENSE})

        ppn, _ = TaxRate.objects.get_or_create(tenant=tenant, name="PPN", defaults={"rate": 11})

        invoice, created = Invoice.objects.get_or_create(
            tenant=tenant, number="INV-0001",
            defaults={
                "customer": company, "issue_date": datetime.date.today(),
                "due_date": datetime.date.today() + datetime.timedelta(days=14),
                "status": Invoice.Status.PAID,
            },
        )
        if created:
            InvoiceItem.objects.create(invoice=invoice, description="Jasa Konsultasi", quantity=1, unit_price=50_000_000, tax_rate=ppn)

        Employee.objects.get_or_create(
            tenant=tenant, name="Siti Aminah",
            defaults={"position": "Staff Finance", "department": "Finance", "base_salary": 8_000_000},
        )

        vendor, _ = Vendor.objects.get_or_create(tenant=tenant, name="PT Sumber Makmur", defaults={"email": "sales@sumbermakmur.co.id"})
        po, created = PurchaseOrder.objects.get_or_create(
            tenant=tenant, po_number="PO-0001",
            defaults={"vendor": vendor, "order_date": datetime.date.today(), "status": PurchaseOrder.Status.SENT},
        )
        if created:
            PurchaseOrderItem.objects.create(purchase_order=po, description="ATK Kantor", quantity=10, unit_price=150_000)
