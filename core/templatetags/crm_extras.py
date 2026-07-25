from django import template

register = template.Library()


@register.filter
def get_attr(obj, field_name):
    value = getattr(obj, field_name, "")
    if callable(value):
        value = value()
    return value


@register.filter
def starts_with(value, prefix):
    return str(value).startswith(prefix)
