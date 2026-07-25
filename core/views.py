from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import TenantRequiredMixin


class GenericTenantListView(TenantRequiredMixin, ListView):
    """List view rendered by the shared templates/core/generic_list.html.

    Subclasses set: model, list_fields = [(label, field_name), ...],
    url_basename = "app:model" (used to build `_create` / `_edit` / `_delete` urls),
    title.
    """

    template_name = "core/generic_list.html"
    paginate_by = 25
    list_fields = []
    url_basename = ""
    title = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.title
        ctx["list_fields"] = self.list_fields
        ctx["url_basename"] = self.url_basename
        ctx["create_url"] = reverse(f"{self.url_basename}_create") if self.url_basename else None
        return ctx


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
        return ctx

    def get_success_url(self):
        return reverse(f"{self.url_basename}_list")

    def form_valid(self, form):
        messages.success(self.request, f"{self.title} berhasil dihapus.")
        return super().form_valid(form)
