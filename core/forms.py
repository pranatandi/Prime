from django import forms


class BootstrapModelForm(forms.ModelForm):
    """Adds Bootstrap classes to every widget automatically.

    Accepts an optional `tenant` kwarg (popped before ModelForm sees it) so
    subclasses can scope FK querysets to the current tenant in __init__.
    """

    def __init__(self, *args, tenant=None, **kwargs):
        self.tenant = tenant
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")
