import json
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import TemplateView

from crm.models import Activity, Deal, PipelineStage
from finance.models import Account, Invoice, JournalEntryLine


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
