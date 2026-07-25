from core.forms import BootstrapModelForm
from .models import Activity, Company, Contact, Deal, PipelineStage


class CompanyForm(BootstrapModelForm):
    class Meta:
        model = Company
        fields = ["name", "industry", "website", "phone", "address", "owner"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].queryset = self.fields["owner"].queryset.filter(tenant=self.tenant)


class ContactForm(BootstrapModelForm):
    class Meta:
        model = Contact
        fields = ["first_name", "last_name", "company", "email", "phone", "position", "notes", "owner"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(tenant=self.tenant)
        self.fields["owner"].queryset = self.fields["owner"].queryset.filter(tenant=self.tenant)


class PipelineStageForm(BootstrapModelForm):
    class Meta:
        model = PipelineStage
        fields = ["name", "order", "is_won", "is_lost"]


class DealForm(BootstrapModelForm):
    class Meta:
        model = Deal
        fields = [
            "title", "company", "contact", "stage", "value", "status",
            "expected_close_date", "owner",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(tenant=self.tenant)
        self.fields["contact"].queryset = Contact.objects.filter(tenant=self.tenant)
        self.fields["stage"].queryset = PipelineStage.objects.filter(tenant=self.tenant)
        self.fields["owner"].queryset = self.fields["owner"].queryset.filter(tenant=self.tenant)
        self.fields["expected_close_date"].widget.attrs["type"] = "date"


class ActivityForm(BootstrapModelForm):
    class Meta:
        model = Activity
        fields = [
            "type", "subject", "notes", "contact", "company", "deal",
            "due_date", "is_done", "assigned_to",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].queryset = Contact.objects.filter(tenant=self.tenant)
        self.fields["company"].queryset = Company.objects.filter(tenant=self.tenant)
        self.fields["deal"].queryset = Deal.objects.filter(tenant=self.tenant)
        self.fields["assigned_to"].queryset = self.fields["assigned_to"].queryset.filter(tenant=self.tenant)
        self.fields["due_date"].widget.attrs["type"] = "date"
