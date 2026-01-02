from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Owner


@receiver(post_save, sender=User)
def create_owner_profile(sender, instance, created, **kwargs):
    """Ensure each user has a matching Owner profile."""
    if created:
        Owner.objects.create(user=instance)
    else:
        Owner.objects.get_or_create(user=instance)
