from django.contrib import admin

from core.admin import TenantScopedAdmin
from .models import Employee, PayrollRun, Payslip


class PayslipInline(admin.TabularInline):
    model = Payslip
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(TenantScopedAdmin):
    list_display = ("name", "position", "department", "base_salary", "is_active", "tenant")
    list_filter = ("tenant", "is_active")
    search_fields = ("name",)


@admin.register(PayrollRun)
class PayrollRunAdmin(TenantScopedAdmin):
    list_display = ("period_start", "period_end", "status", "total_net_pay", "tenant")
    list_filter = ("tenant", "status")
    inlines = [PayslipInline]
