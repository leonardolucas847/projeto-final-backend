from django.contrib.auth import get_user_model
from rest_framework import serializers

# Importa o modelo Profile do diretório models/profile.py
from accounts.models.profile import Profile

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):

  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'password')
    extra_kwargs = {'password': {'write_only': True}}

  def create(self, validated_data):
    return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
  avatar = serializers.ImageField(
      source='profile.avatar', required=False, allow_null=True
  )
  bio = serializers.CharField(
      source='profile.bio', required=False, allow_blank=True
  )
  # Mapeia a lista de perfis seguidos como IDs via Serializer Field do DRF
  following = serializers.PrimaryKeyRelatedField(
      many=True, read_only=True, source='profile.following'
  )

  class Meta:
    model = User
    fields = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'avatar',
        'following',
    )
    extra_kwargs = {'username': {'read_only': True}}

  def update(self, instance, validated_data):
    # O DRF extrai os campos com source='profile.x' para um dicionário chamado 'profile'
    profile_data = validated_data.pop('profile', {})
    instance = super().update(instance, validated_data)

    # Busca ou cria o perfil garantindo que não ocorra DoesNotExist
    profile, _ = Profile.objects.get_or_create(user=instance)

    if 'avatar' in profile_data:
      profile.avatar = profile_data['avatar']
    if 'bio' in profile_data:
      profile.bio = profile_data['bio']

    profile.save()
    return instance


class ChangePasswordSerializer(serializers.Serializer):
  old_password = serializers.CharField(required=True, write_only=True)
  new_password = serializers.CharField(required=True, write_only=True)

  def validate_old_password(self, value):
    user = self.context['request'].user
    if not user.check_password(value):
      raise serializers.ValidationError('A senha atual está incorreta.')
    return value