from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, Transaction, Vehicle
from django.contrib.auth.models import User



@receiver(post_save, sender=User)
def creat_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, phone_number='', location='')


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

