import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from core.views import (
    GenericTenantCreateView,
    GenericTenantDeleteView,
    GenericTenantListView,
    GenericTenantUpdateView,
    TenantCSVExportView,
)
from .forms import ActivityForm, CompanyForm, ContactForm, DealForm, PipelineStageForm
from .models import Activity, Company, Contact, Deal, PipelineStage


# ---- Company ----

class CompanyListView(GenericTenantListView):
    model = Company
    title = "Companies"
    url_basename = "crm:company"
    has_export = True
    list_fields = [("Nama", "name"), ("Industri", "industry"), ("Telepon", "phone"), ("Owner", "owner")]


class CompanyCreateView(GenericTenantCreateView):
    model = Company
    form_class = CompanyForm
    title = "Company"
    url_basename = "crm:company"


class CompanyUpdateView(GenericTenantUpdateView):
    model = Company
    form_class = CompanyForm
    title = "Company"
    url_basename = "crm:company"


class CompanyDeleteView(GenericTenantDeleteView):
    model = Company
    title = "Company"
    url_basename = "crm:company"


# ---- Contact ----

class ContactListView(GenericTenantListView):
    model = Contact
    title = "Contacts"
    url_basename = "crm:contact"
    has_export = True
    list_fields = [("Nama", "full_name"), ("Company", "company"), ("Email", "email"), ("Telepon", "phone")]


class ContactCreateView(GenericTenantCreateView):
    model = Contact
    form_class = ContactForm
    title = "Contact"
    url_basename = "crm:contact"


class ContactUpdateView(GenericTenantUpdateView):
    model = Contact
    form_class = ContactForm
    title = "Contact"
    url_basename = "crm:contact"


class ContactDeleteView(GenericTenantDeleteView):
    model = Contact
    title = "Contact"
    url_basename = "crm:contact"


# ---- Pipeline Stage ----

class PipelineStageListView(GenericTenantListView):
    model = PipelineStage
    title = "Pipeline Stages"
    url_basename = "crm:stage"
    list_fields = [("Nama", "name"), ("Urutan", "order"), ("Won?", "is_won"), ("Lost?", "is_lost")]


class PipelineStageCreateView(GenericTenantCreateView):
    model = PipelineStage
    form_class = PipelineStageForm
    title = "Pipeline Stage"
    url_basename = "crm:stage"


class PipelineStageUpdateView(GenericTenantUpdateView):
    model = PipelineStage
    form_class = PipelineStageForm
    title = "Pipeline Stage"
    url_basename = "crm:stage"


class PipelineStageDeleteView(GenericTenantDeleteView):
    model = PipelineStage
    title = "Pipeline Stage"
    url_basename = "crm:stage"


# ---- Deal (Kanban board is the primary view) ----

class DealBoardView(LoginRequiredMixin, TemplateView):
    template_name = "crm/deal_board.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        ctx["stages"] = PipelineStage.objects.filter(tenant=tenant).prefetch_related("deals")
        return ctx


class DealMoveStageView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tenant = request.user.tenant
        deal = Deal.objects.filter(tenant=tenant, pk=pk).first()
        if not deal:
            return JsonResponse({"ok": False, "error": "Deal tidak ditemukan"}, status=404)
        payload = json.loads(request.body or "{}")
        stage = PipelineStage.objects.filter(tenant=tenant, pk=payload.get("stage_id")).first()
        if not stage:
            return JsonResponse({"ok": False, "error": "Stage tidak valid"}, status=400)
        deal.stage = stage
        if stage.is_won:
            deal.status = Deal.Status.WON
        elif stage.is_lost:
            deal.status = Deal.Status.LOST
        else:
            deal.status = Deal.Status.OPEN
        deal.save()
        return JsonResponse({"ok": True})


class DealCreateView(GenericTenantCreateView):
    model = Deal
    form_class = DealForm
    title = "Deal"
    url_basename = "crm:deal"

    def get_success_url(self):
        return reverse("crm:deal_board")


class DealUpdateView(GenericTenantUpdateView):
    model = Deal
    form_class = DealForm
    title = "Deal"
    url_basename = "crm:deal"

    def get_success_url(self):
        return reverse("crm:deal_board")


class DealDeleteView(GenericTenantDeleteView):
    model = Deal
    title = "Deal"
    url_basename = "crm:deal"

    def get_success_url(self):
        return reverse("crm:deal_board")


# ---- Activity ----

class ActivityListView(GenericTenantListView):
    model = Activity
    title = "Tasks & Activities"
    url_basename = "crm:activity"
    has_export = True
    list_fields = [
        ("Tipe", "get_type_display"), ("Subjek", "subject"), ("Jatuh Tempo", "due_date"),
        ("Selesai?", "is_done"), ("PIC", "assigned_to"),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("assigned_to")


class ActivityCreateView(GenericTenantCreateView):
    model = Activity
    form_class = ActivityForm
    title = "Activity"
    url_basename = "crm:activity"


class ActivityUpdateView(GenericTenantUpdateView):
    model = Activity
    form_class = ActivityForm
    title = "Activity"
    url_basename = "crm:activity"


class ActivityDeleteView(GenericTenantDeleteView):
    model = Activity
    title = "Activity"
    url_basename = "crm:activity"


# ---- CSV Export ----

class CompanyExportView(TenantCSVExportView):
    model = Company
    filename = "companies"
    export_fields = [("Nama", "name"), ("Industri", "industry"), ("Website", "website"), ("Telepon", "phone"), ("Owner", "owner")]


class ContactExportView(TenantCSVExportView):
    model = Contact
    filename = "contacts"
    export_fields = [("Nama", "full_name"), ("Company", "company"), ("Email", "email"), ("Telepon", "phone"), ("Posisi", "position")]


class DealExportView(TenantCSVExportView):
    model = Deal
    filename = "deals"
    export_fields = [
        ("Judul", "title"), ("Company", "company"), ("Stage", "stage"), ("Nilai", "value"),
        ("Status", "get_status_display"), ("Owner", "owner"), ("Target Closing", "expected_close_date"),
    ]


class ActivityExportView(TenantCSVExportView):
    model = Activity
    filename = "activities"
    export_fields = [
        ("Tipe", "get_type_display"), ("Subjek", "subject"), ("Jatuh Tempo", "due_date"),
        ("Selesai?", "is_done"), ("PIC", "assigned_to"),
    ]
