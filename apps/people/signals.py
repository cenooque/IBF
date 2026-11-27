from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Pessoa


@receiver(post_save, sender=Pessoa)
def sincronizar_conjuge_pessoa(sender, instance: Pessoa, **kwargs):
    """Garante espelhamento bidirecional de cônjuge quando salvo via signal."""
    if getattr(instance, "_sincronizando_conjuge", False):
        return

    if instance.conjuge_id:
        conjuge = Pessoa.objects.filter(pk=instance.conjuge_id).first()
        if conjuge and conjuge.conjuge_id != instance.pk:
            conjuge.conjuge = instance
            conjuge._sincronizando_conjuge = True
            conjuge.save(update_fields=["conjuge", "atualizado_em"])