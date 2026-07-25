from core.forms import BootstrapModelForm
from .models import Employee, PayrollRun


class EmployeeForm(BootstrapModelForm):
    class Meta:
        model = Employee
        fields = ["name", "position", "department", "hire_date", "base_salary", "bank_account", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hire_date"].widget.attrs["type"] = "date"


class PayrollRunForm(BootstrapModelForm):
    class Meta:
        model = PayrollRun
        fields = ["period_start", "period_end", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["period_start"].widget.attrs["type"] = "date"
        self.fields["period_end"].widget.attrs["type"] = "date"
