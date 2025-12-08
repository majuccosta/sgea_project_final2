from django.db.models.signals import post_save, post_delete, m2m_changed
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

# Log quando usuário é atualizado
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

# Log quando evento é criado
@receiver(post_save, sender=Event)
def log_evento_criado(sender, instance, created, **kwargs):
    if created:
        registrar_log(
            user=None,
            action="CREATE",
            model="Event",
            object_id=instance.id,
            description=f"Evento criado: {instance.title}"
        )

# Log quando evento é atualizado
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

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import registrar_log
from .models import Event, Registration

User = get_user_model()

@receiver(m2m_changed, sender=Event.participants.through)
def sync_registration(sender, instance, action, pk_set, **kwargs):
    if action not in ["post_add", "post_remove"]:
        return

    for user_id in pk_set:
        user = User.objects.get(id=user_id)
        if action == "post_add":
            # cria registro de inscrição
            Registration.objects.get_or_create(user=user, event=instance)
            registrar_log(
                user=user,
                action="CREATE",
                model="Registration",
                object_id=f"{user.id}-{instance.id}",
                description=f"Usuário {user.username} inscrito no evento {instance.title}"
            )
        elif action == "post_remove":
            # remove registro de inscrição
            Registration.objects.filter(user=user, event=instance).delete()
            registrar_log(
                user=user,
                action="DELETE",
                model="Registration",
                object_id=f"{user.id}-{instance.id}",
                description=f"Usuário {user.username} cancelou inscrição no evento {instance.title}"
            )
