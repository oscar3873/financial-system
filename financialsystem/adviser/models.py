import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

import os

def default_avatar(adviser):
    try:
        first_letter = adviser.user.first_name[0].upper()
    except:
        first_letter = adviser.user.username[0].upper()

    avatar_path = os.path.join('avatares', f'{first_letter}.png')
    print("----------------", avatar_path)
    return avatar_path


# Create your models here.
class Adviser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="adviser", default=default_avatar)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return "{}, {}".format(self.user.first_name, self.user.last_name)
    
    class Meta:
        ordering = ['-created_at']
    
# signals
def ensure_profile_exists(sender, instance, **kwargs):
    if kwargs.get('created', False):
        adviser, created = Adviser.objects.get_or_create(user=instance)
        if created:
            avatar_path = default_avatar(adviser)
            adviser.avatar = avatar_path
            adviser.save()
        print("Se acaba de crear un usuario y un asesor")


post_save.connect(ensure_profile_exists, sender=User)



