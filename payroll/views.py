from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView

from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
    TenantCSVExportView,
)
from .forms import EmployeeForm, PayrollRunForm
from .models import Employee, PayrollRun, Payslip


# ---- Employees ----

class EmployeeListView(GenericTenantListView):
    model = Employee
    title = "Employees"
    url_basename = "payroll:employee"
    has_export = True
    list_fields = [
        ("Nama", "name"), ("Posisi", "position"), ("Departemen", "department"),
        ("Gaji Pokok", "base_salary"), ("Aktif", "is_active"),
    ]


class EmployeeCreateView(GenericTenantCreateView):
    model = Employee
    form_class = EmployeeForm
    title = "Employee"
    url_basename = "payroll:employee"


class EmployeeUpdateView(GenericTenantUpdateView):
    model = Employee
    form_class = EmployeeForm
    title = "Employee"
    url_basename = "payroll:employee"


class EmployeeDeleteView(GenericTenantDeleteView):
    model = Employee
    title = "Employee"
    url_basename = "payroll:employee"


# ---- Payroll Runs ----

class PayrollRunListView(GenericTenantListView):
    model = PayrollRun
    title = "Payroll Runs"
    url_basename = "payroll:payrollrun"
    template_name = "payroll/payrollrun_list.html"


class PayrollRunCreateView(GenericTenantCreateView):
    model = PayrollRun
    form_class = PayrollRunForm
    title = "Payroll Run"
    url_basename = "payroll:payrollrun"


class PayrollRunUpdateView(GenericTenantUpdateView):
    model = PayrollRun
    form_class = PayrollRunForm
    title = "Payroll Run"
    url_basename = "payroll:payrollrun"


class PayrollRunDeleteView(GenericTenantDeleteView):
    model = PayrollRun
    title = "Payroll Run"
    url_basename = "payroll:payrollrun"


class PayrollRunDetailView(LoginRequiredMixin, DetailView):
    model = PayrollRun
    template_name = "payroll/payrollrun_detail.html"
    context_object_name = "run"

    def get_queryset(self):
        return PayrollRun.objects.filter(tenant=self.request.user.tenant).prefetch_related("payslips__employee")


class PayrollRunProcessView(LoginRequiredMixin, View):
    def post(self, request, pk):
        run = get_object_or_404(PayrollRun, pk=pk, tenant=request.user.tenant)
        employees = Employee.objects.filter(tenant=request.user.tenant, is_active=True)
        created = 0
        for employee in employees:
            _, was_created = Payslip.objects.get_or_create(
                run=run, employee=employee,
                defaults={"base_salary": employee.base_salary, "allowances": 0, "deductions": 0},
            )
            if was_created:
                created += 1
        run.status = PayrollRun.Status.PROCESSED
        run.processed_at = timezone.now()
        run.save()
        messages.success(request, f"Payroll run diproses: {created} payslip dibuat.")
        return redirect("payroll:payrollrun_detail", pk=run.pk)


# ---- CSV Export ----

class EmployeeExportView(TenantCSVExportView):
    model = Employee
    filename = "employees"
    export_fields = [
        ("Nama", "name"), ("Posisi", "position"), ("Departemen", "department"),
        ("Tgl Masuk", "hire_date"), ("Gaji Pokok", "base_salary"), ("Aktif", "is_active"),
    ]
