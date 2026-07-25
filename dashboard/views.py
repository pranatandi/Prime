import json
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.views.generic import TemplateView

from crm.models import Activity, Company, Contact, Deal, PipelineStage
from finance.models import Account, Invoice, JournalEntryLine


def _last_n_month_starts(today, n):
    """Return the first-of-month date for each of the last n months, oldest first."""
    months = []
    year, month = today.year, today.month
    for _ in range(n):
        months.append(today.replace(year=year, month=month, day=1))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        today = timezone.localdate()
        month_start = today.replace(day=1)

        stages = PipelineStage.objects.filter(tenant=tenant).order_by("order")
        funnel = []
        for stage in stages:
            total = stage.deals.filter(status=Deal.Status.OPEN).aggregate(s=Sum("value"))["s"] or Decimal("0")
            funnel.append({"stage": stage.name, "total": float(total), "count": stage.deals.filter(status=Deal.Status.OPEN).count()})

        won_this_month = Deal.objects.filter(
            tenant=tenant, status=Deal.Status.WON, updated_at__date__gte=month_start,
        )
        won_total = won_this_month.aggregate(s=Sum("value"))["s"] or Decimal("0")

        open_deals = Deal.objects.filter(tenant=tenant, status=Deal.Status.OPEN)
        open_total = open_deals.aggregate(s=Sum("value"))["s"] or Decimal("0")

        tasks_due_today = Activity.objects.filter(tenant=tenant, is_done=False, due_date=today).select_related("assigned_to")
        overdue_tasks = Activity.objects.filter(tenant=tenant, is_done=False, due_date__lt=today).count()

        revenue_this_month = Invoice.objects.filter(
            tenant=tenant, status=Invoice.Status.PAID, issue_date__gte=month_start,
        )
        revenue_total = sum((inv.total for inv in revenue_this_month), Decimal("0"))

        expense_lines = JournalEntryLine.objects.filter(
            entry__tenant=tenant, account__type=Account.AccountType.EXPENSE, entry__date__gte=month_start,
        )
        expense_total = expense_lines.aggregate(s=Sum("debit"))["s"] or Decimal("0")

        ctx.update({
            "open_deal_count": open_deals.count(),
            "open_deal_total": open_total,
            "won_deal_count": won_this_month.count(),
            "won_deal_total": won_total,
            "tasks_due_today": tasks_due_today,
            "overdue_tasks": overdue_tasks,
            "revenue_this_month": revenue_total,
            "expense_this_month": expense_total,
            "funnel_labels": json.dumps([f["stage"] for f in funnel]),
            "funnel_values": json.dumps([f["total"] for f in funnel]),
        })
        return ctx


class SalesReportView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/sales_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        today = timezone.localdate()
        months = _last_n_month_starts(today, 6)

        closed = Deal.objects.filter(tenant=tenant, status__in=[Deal.Status.WON, Deal.Status.LOST])
        won_count = closed.filter(status=Deal.Status.WON).count()
        lost_count = closed.filter(status=Deal.Status.LOST).count()
        win_rate = round(won_count / (won_count + lost_count) * 100, 1) if (won_count + lost_count) else 0
        avg_deal_size = Deal.objects.filter(tenant=tenant, status=Deal.Status.WON).aggregate(avg=Avg("value"))["avg"] or Decimal("0")

        by_owner = (
            Deal.objects.filter(tenant=tenant)
            .values("owner__username", "owner_id")
            .annotate(count=Count("id"), total=Sum("value"))
            .order_by("-total")
        )

        monthly_rows = (
            Deal.objects.filter(tenant=tenant, status=Deal.Status.WON, updated_at__date__gte=months[0])
            .annotate(month=TruncMonth("updated_at"))
            .values("month")
            .annotate(total=Sum("value"))
        )
        monthly_totals = {row["month"].date() if hasattr(row["month"], "date") else row["month"]: row["total"] for row in monthly_rows}
        trend_labels = [m.strftime("%b %Y") for m in months]
        trend_values = [float(monthly_totals.get(m, 0) or 0) for m in months]

        ctx.update({
            "won_count": won_count,
            "lost_count": lost_count,
            "win_rate": win_rate,
            "avg_deal_size": avg_deal_size,
            "by_owner": by_owner,
            "trend_labels": json.dumps(trend_labels),
            "trend_values": json.dumps(trend_values),
        })
        return ctx


class FinancialReportView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/financial_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        today = timezone.localdate()
        months = _last_n_month_starts(today, 6)

        def monthly_net(account_type, credit_is_increase):
            rows = (
                JournalEntryLine.objects.filter(
                    entry__tenant=tenant, account__type=account_type, entry__date__gte=months[0],
                )
                .annotate(month=TruncMonth("entry__date"))
                .values("month")
                .annotate(debit=Sum("debit"), credit=Sum("credit"))
            )
            totals = {}
            for row in rows:
                month = row["month"].date() if hasattr(row["month"], "date") else row["month"]
                debit = row["debit"] or Decimal("0")
                credit = row["credit"] or Decimal("0")
                totals[month] = (credit - debit) if credit_is_increase else (debit - credit)
            return [float(totals.get(m, 0) or 0) for m in months]

        income_series = monthly_net(Account.AccountType.INCOME, credit_is_increase=True)
        expense_series = monthly_net(Account.AccountType.EXPENSE, credit_is_increase=False)

        unpaid_invoices = Invoice.objects.filter(tenant=tenant).exclude(status=Invoice.Status.PAID).select_related("customer")
        aging = {"Belum jatuh tempo": Decimal("0"), "1-30 hari": Decimal("0"), "31-60 hari": Decimal("0"), ">60 hari": Decimal("0")}
        for inv in unpaid_invoices:
            days_overdue = (today - inv.due_date).days
            if days_overdue <= 0:
                aging["Belum jatuh tempo"] += inv.total
            elif days_overdue <= 30:
                aging["1-30 hari"] += inv.total
            elif days_overdue <= 60:
                aging["31-60 hari"] += inv.total
            else:
                aging[">60 hari"] += inv.total

        ctx.update({
            "month_labels": json.dumps([m.strftime("%b %Y") for m in months]),
            "income_series": json.dumps(income_series),
            "expense_series": json.dumps(expense_series),
            "aging": aging,
            "unpaid_invoices": unpaid_invoices,
        })
        return ctx


class GlobalSearchView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/search_results.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        query = self.request.GET.get("q", "").strip()
        ctx["query"] = query
        if not query:
            return ctx

        ctx["companies"] = Company.objects.filter(tenant=tenant, name__icontains=query)[:10]
        ctx["contacts"] = Contact.objects.filter(tenant=tenant).filter(
            first_name__icontains=query
        ) | Contact.objects.filter(tenant=tenant, last_name__icontains=query) | Contact.objects.filter(
            tenant=tenant, email__icontains=query
        )
        ctx["contacts"] = ctx["contacts"].distinct()[:10]
        ctx["deals"] = Deal.objects.filter(tenant=tenant, title__icontains=query)[:10]
        ctx["invoices"] = Invoice.objects.filter(tenant=tenant, number__icontains=query)[:10]
        return ctx
