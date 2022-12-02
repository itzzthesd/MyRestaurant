from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, userProfile


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created,**kwargs):
    print('signals called')
    if created:
        userProfile.objects.create(user=instance)
        print('user profile is created')
    else:
        try:
            profile = userProfile.objects.get(user=instance)
            profile.save()
        except:
            userProfile.objects.create(user=instance)
        print('user is updated')