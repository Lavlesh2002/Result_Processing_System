from .models import AuditLog

def log_action(user, action, model_name, object_id=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id
    )