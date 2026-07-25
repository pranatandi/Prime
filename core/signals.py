from django.db.models.signals import post_delete, post_save

from core.middleware import get_current_user
from core.models import AuditLog


def _log(instance, action):
    tenant = getattr(instance, "tenant", None)
    if tenant is None:
        return
    user = get_current_user()
    if user is not None and not getattr(user, "is_authenticated", False):
        user = None
    AuditLog.objects.create(
        tenant=tenant,
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_repr=str(instance)[:255],
    )


def _post_save_handler(sender, instance, created, **kwargs):
    _log(instance, AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE)


def _post_delete_handler(sender, instance, **kwargs):
    _log(instance, AuditLog.Action.DELETE)


def connect_audit_log(models):
    for model in models:
        post_save.connect(_post_save_handler, sender=model, dispatch_uid=f"auditlog_save_{model.__name__}")
        post_delete.connect(_post_delete_handler, sender=model, dispatch_uid=f"auditlog_delete_{model.__name__}")
