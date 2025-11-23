from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import registrar_log
from .models import Event

User = get_user_model()

# Log quando usuário é criado
@receiver(post_save, sender=User)
def log_criacao_usuario(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            user=instance,
            action="CREATE",
            model="User",
            object_id=instance.id,
            description=f"Usuário criado: {instance.email}"
        )

# Log quando evento é criado
@receiver(post_save, sender=Event)
def log_evento_criado(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            user=None,  # caso evento não seja criado via painel autenticado
            action="CREATE",
            model="Event",
            object_id=instance.id,
            description=f"Evento criado: {instance.title}"
        )

# Log quando evento é apagado
@receiver(post_delete, sender=Event)
def log_evento_apagado(sender, instance, **kwargs):
    registrar_log(
        user=None,
        action="DELETE",
        model="Event",
        object_id=instance.id,
        description=f"Evento apagado: {instance.title}"
    )
@receiver(post_save, sender=User)
def log_update_usuario(sender, instance, created, **kwargs):
    if not created:
        registrar_log(
            user=instance,
            action="UPDATE",
            model="User",
            object_id=instance.id,
            description=f"Usuário atualizado: {instance.email}"
        )
@receiver(post_save, sender=Event)
def log_evento_atualizado(sender, instance, created, **kwargs):
    if not created:
        registrar_log(
            user=None,
            action="UPDATE",
            model="Event",
            object_id=instance.id,
            description=f"Evento atualizado: {instance.title}"
        )
