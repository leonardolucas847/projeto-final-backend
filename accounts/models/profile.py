from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Profile(models.Model):
  user = models.OneToOneField(
      User, on_delete=models.CASCADE, related_name='profile'
  )
  avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
  bio = models.TextField(blank=True, default='')
  following = models.ManyToManyField(
      'self', symmetrical=False, related_name='followers', blank=True
  )

  def __str__(self):
    return f'Perfil de {self.user.username}'


# Signal para criar/salvar automaticamente o Profile sempre que um User for criado
@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)
  else:
    if hasattr(instance, 'profile'):
      instance.profile.save()