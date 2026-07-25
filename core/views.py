import csv

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import TenantRequiredMixin

SECTION_LABELS = {
    "crm": "CRM",
    "finance": "Finance",
    "payroll": "Payroll",
    "purchasing": "Purchasing",
    "accounts": "Admin",
    "dashboard": "Dashboard",
}


def _section_label(url_basename):
    namespace = url_basename.split(":")[0] if url_basename else ""
    return SECTION_LABELS.get(namespace, namespace.title())


def _breadcrumbs(url_basename, title):
    crumbs = [("Dashboard", reverse("dashboard:index"))]
    section = _section_label(url_basename)
    if section:
        crumbs.append((section, None))
    crumbs.append((title, None))
    return crumbs


class GenericTenantListView(TenantRequiredMixin, ListView):
    """List view rendered by the shared templates/core/generic_list.html.

    Subclasses set: model, list_fields = [(label, field_name), ...],
    url_basename = "app:model" (used to build `_create` / `_edit` / `_delete` urls),
    title. Set `has_export = True` to show an "Export CSV" button pointing at
    `<url_basename>_export` (must be wired up alongside a TenantCSVExportView).
    Set `readonly = True` to hide the Edit/Hapus action column (e.g. Audit Log).
    """

    template_name = "core/generic_list.html"
    paginate_by = 25
    list_fields = []
    url_basename = ""
    title = ""
    has_export = False
    readonly = False

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.title
        ctx["list_fields"] = self.list_fields
        ctx["url_basename"] = self.url_basename
        ctx["readonly"] = self.readonly
        ctx["create_url"] = reverse(f"{self.url_basename}_create") if self.url_basename and not self.readonly else None
        ctx["export_url"] = reverse(f"{self.url_basename}_export") if self.has_export else None
        ctx["breadcrumbs"] = _breadcrumbs(self.url_basename, self.title)
        return ctx


class TenantCSVExportView(TenantRequiredMixin, ListView):
    """Streams the tenant-scoped queryset as CSV.

    Subclasses set: model, export_fields = [(header, field_name), ...],
    filename (without extension).
    """

    export_fields = []
    filename = "export"

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{self.filename}.csv"'
        writer = csv.writer(response)
        writer.writerow([label for label, _ in self.export_fields])
        for obj in self.get_queryset():
            row = []
            for _, field_name in self.export_fields:
                value = getattr(obj, field_name, "")
                if callable(value):
                    value = value()
                row.append(value)
            writer.writerow(row)
        return response


class GenericTenantCreateView(TenantRequiredMixin, CreateView):
    template_name = "core/generic_form.html"
    title = ""
    url_basename = ""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.user.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Tambah {self.title}"
        ctx["cancel_url"] = self.get_success_url()
        ctx["breadcrumbs"] = _breadcrumbs(self.url_basename, ctx["title"])
        return ctx

    def get_success_url(self):
        return reverse(f"{self.url_basename}_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"{self.title} berhasil ditambahkan.")
        return response


class GenericTenantUpdateView(TenantRequiredMixin, UpdateView):
    template_name = "core/generic_form.html"
    title = ""
    url_basename = ""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.user.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Edit {self.title}"
        ctx["cancel_url"] = self.get_success_url()
        ctx["breadcrumbs"] = _breadcrumbs(self.url_basename, ctx["title"])
        return ctx

    def get_success_url(self):
        return reverse(f"{self.url_basename}_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"{self.title} berhasil diperbarui.")
        return response


class TenantFormsetMixin:
    """Mixin for Create/UpdateView subclasses that also manage an inline formset.

    Subclasses set `formset_class` (an inlineformset_factory result) and
    `formset_template_name` (rendered inside the `formset` block of
    core/generic_form.html).
    """

    formset_class = None

    def get_formset(self, instance=None):
        FormsetClass = self.formset_class
        kwargs = {"instance": instance, "form_kwargs": {"tenant": self.request.user.tenant}}
        if self.request.method == "POST":
            return FormsetClass(self.request.POST, **kwargs)
        return FormsetClass(**kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if "formset" not in ctx:
            ctx["formset"] = self.get_formset(getattr(self, "object", None))
        return ctx

    def form_valid(self, form):
        # Validate the formset against the (possibly unsaved) parent instance
        # before writing anything, so an invalid formset never leaves behind
        # an orphaned parent row.
        formset = self.formset_class(
            self.request.POST, instance=form.instance, form_kwargs={"tenant": self.request.user.tenant}
        )
        if not formset.is_valid():
            ctx = self.get_context_data(form=form)
            ctx["formset"] = formset
            return render(self.request, self.template_name, ctx)

        self.object = form.save(commit=False)
        if hasattr(self.object, "tenant_id"):
            self.object.tenant = self.request.user.tenant
        self.object.save()
        form.save_m2m()
        formset.instance = self.object
        formset.save()
        messages.success(self.request, f"{self.title} berhasil disimpan.")
        return HttpResponseRedirect(self.get_success_url())


class GenericTenantDeleteView(TenantRequiredMixin, DeleteView):
    template_name = "core/generic_confirm_delete.html"
    title = ""
    url_basename = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.title
        ctx["cancel_url"] = self.get_success_url()
        ctx["breadcrumbs"] = _breadcrumbs(self.url_basename, f"Hapus {self.title}")
        return ctx

    def get_success_url(self):
        return reverse(f"{self.url_basename}_list")

    def form_valid(self, form):
        messages.success(self.request, f"{self.title} berhasil dihapus.")
        return super().form_valid(form)
