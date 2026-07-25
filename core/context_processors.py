from django.utils import timezone


def nav_notifications(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated or not user.tenant_id:
        return {}

    from crm.models import Activity
    from finance.models import Invoice

    today = timezone.localdate()
    tasks = (
        Activity.objects.filter(tenant=user.tenant, is_done=False, due_date__isnull=False, due_date__lte=today)
        .select_related("assigned_to")
        .order_by("due_date")[:8]
    )
    overdue_invoices = (
        Invoice.objects.filter(tenant=user.tenant, due_date__lt=today)
        .exclude(status=Invoice.Status.PAID)
        .select_related("customer")
        .order_by("due_date")[:8]
    )
    return {
        "nav_tasks": tasks,
        "nav_overdue_invoices": overdue_invoices,
        "nav_notification_count": len(tasks) + len(overdue_invoices),
    }
