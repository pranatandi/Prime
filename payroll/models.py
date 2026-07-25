from decimal import Decimal

from django.db import models

from core.models import TenantScopedModel


class Employee(TenantScopedModel):
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    base_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    bank_account = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PayrollRun(TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PROCESSED = "PROCESSED", "Processed"
        PAID = "PAID", "Paid"

    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-period_start"]

    def __str__(self):
        return f"Payroll {self.period_start} - {self.period_end}"

    @property
    def total_net_pay(self):
        return sum((p.net_pay for p in self.payslips.all()), Decimal("0"))


class Payslip(models.Model):
    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="payslips")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="payslips")
    base_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["employee__name"]

    def __str__(self):
        return f"{self.employee} - {self.run}"

    def save(self, *args, **kwargs):
        self.net_pay = self.base_salary + self.allowances - self.deductions
        super().save(*args, **kwargs)
