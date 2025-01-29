# signals.py
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import User

@receiver(pre_delete, sender=User)
def delete_related_objects(sender, instance, **kwargs):
    if instance.company:
        instance.company.delete()
    if instance.Student:
        instance.Student.delete()