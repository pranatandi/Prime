from django import template
from django.utils.html import format_html

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


_BADGE_COLORS = {
    "won": "success", "paid": "success", "processed": "success", "received": "success",
    "active": "success", "aktif": "success",
    "lost": "danger", "overdue": "danger", "cancelled": "danger", "canceled": "danger",
    "draft": "warning", "pending": "warning",
    "sent": "info", "open": "info",
}


@register.filter
def smart_badge(value):
    """Wraps recognizable status text / booleans in a colored Bootstrap badge.

    Unrecognized values pass through unchanged, so it's safe to apply to any
    generic table cell without knowing in advance whether it holds a status.
    """
    if value is True:
        return format_html('<span class="badge rounded-pill bg-success-subtle text-success-emphasis">Ya</span>')
    if value is False:
        return format_html('<span class="badge rounded-pill bg-secondary-subtle text-secondary-emphasis">Tidak</span>')
    text = str(value).strip()
    color = _BADGE_COLORS.get(text.lower())
    if not color:
        return value
    return format_html(
        '<span class="badge rounded-pill bg-{}-subtle text-{}-emphasis">{}</span>', color, color, text,
    )
