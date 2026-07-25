from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import Tenant
from finance.models import Account
from .models import DepreciationEntry, FixedAsset


class FixedAssetDepreciationTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.user = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant, role=User.Role.ADMIN,
        )
        self.asset_account = Account.objects.create(
            tenant=self.tenant, code="1500", name="Peralatan Kantor", type=Account.AccountType.ASSET,
        )
        self.accum_account = Account.objects.create(
            tenant=self.tenant, code="1510", name="Akum. Penyusutan Peralatan", type=Account.AccountType.ASSET,
        )
        self.expense_account = Account.objects.create(
            tenant=self.tenant, code="6100", name="Beban Penyusutan", type=Account.AccountType.EXPENSE,
        )
        self.asset = FixedAsset.objects.create(
            tenant=self.tenant, asset_number="FA-0001", name="Laptop", acquisition_date="2026-01-01",
            acquisition_cost=Decimal("12000000"), salvage_value=Decimal("0"), useful_life_months=24,
            asset_account=self.asset_account, accumulated_depreciation_account=self.accum_account,
            depreciation_expense_account=self.expense_account,
        )
        self.client.login(username="user_a", password="pass12345")

    def test_post_depreciation_creates_journal_and_reduces_book_value(self):
        response = self.client.post(reverse("assets:fixedasset_post_depreciation", args=[self.asset.pk]))
        self.assertEqual(response.status_code, 302)

        entry = DepreciationEntry.objects.get(fixed_asset=self.asset)
        self.assertEqual(entry.amount, Decimal("500000"))  # 12,000,000 / 24

        lines = list(entry.journal_entry.lines.all())
        expense_line = next(l for l in lines if l.account_id == self.expense_account.pk)
        accum_line = next(l for l in lines if l.account_id == self.accum_account.pk)
        self.assertEqual(expense_line.debit, Decimal("500000"))
        self.assertEqual(accum_line.credit, Decimal("500000"))

        self.assertEqual(self.asset.book_value, Decimal("11500000"))

    def test_double_posting_same_period_is_blocked(self):
        self.client.post(reverse("assets:fixedasset_post_depreciation", args=[self.asset.pk]))
        self.client.post(reverse("assets:fixedasset_post_depreciation", args=[self.asset.pk]))
        self.assertEqual(DepreciationEntry.objects.filter(fixed_asset=self.asset).count(), 1)

    def test_dispose_sets_status(self):
        response = self.client.post(reverse("assets:fixedasset_dispose", args=[self.asset.pk]))
        self.assertEqual(response.status_code, 302)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, FixedAsset.Status.DISPOSED)
        self.assertIsNotNone(self.asset.disposal_date)


class FixedAssetTenantIsolationTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A")
        self.tenant_b = Tenant.objects.create(name="Tenant B")
        self.user_a = User.objects.create_user(
            username="user_a", password="pass12345", tenant=self.tenant_a, role=User.Role.ADMIN,
        )

        def make_accounts(tenant):
            asset_acc = Account.objects.create(tenant=tenant, code="1500", name="Peralatan", type=Account.AccountType.ASSET)
            accum_acc = Account.objects.create(tenant=tenant, code="1510", name="Akum. Penyusutan", type=Account.AccountType.ASSET)
            exp_acc = Account.objects.create(tenant=tenant, code="6100", name="Beban Penyusutan", type=Account.AccountType.EXPENSE)
            return asset_acc, accum_acc, exp_acc

        asset_acc_a, accum_acc_a, exp_acc_a = make_accounts(self.tenant_a)
        asset_acc_b, accum_acc_b, exp_acc_b = make_accounts(self.tenant_b)

        FixedAsset.objects.create(
            tenant=self.tenant_a, asset_number="FA-A", name="Asset A", acquisition_date="2026-01-01",
            acquisition_cost=Decimal("1000000"), useful_life_months=12,
            asset_account=asset_acc_a, accumulated_depreciation_account=accum_acc_a, depreciation_expense_account=exp_acc_a,
        )
        FixedAsset.objects.create(
            tenant=self.tenant_b, asset_number="FA-B", name="Asset B", acquisition_date="2026-01-01",
            acquisition_cost=Decimal("1000000"), useful_life_months=12,
            asset_account=asset_acc_b, accumulated_depreciation_account=accum_acc_b, depreciation_expense_account=exp_acc_b,
        )
        self.client.login(username="user_a", password="pass12345")

    def test_list_only_shows_own_tenant(self):
        response = self.client.get(reverse("assets:fixedasset_list"))
        self.assertContains(response, "Asset A")
        self.assertNotContains(response, "Asset B")
