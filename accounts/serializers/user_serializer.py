from django.contrib.auth import get_user_model
from rest_framework import serializers

# Importa o modelo Profile do diretório models/profile.py
from accounts.models.profile import Profile
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source='user.email', required=False, allow_blank=True
    )
    first_name = serializers.CharField(
        source='user.first_name', required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source='user.last_name', required=False, allow_blank=True
    )
    avatar = serializers.ImageField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    following = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = Profile
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'bio',
            'avatar',
            'following',
        )

    def update(self, instance, validated_data):
        # 1. Extrai os dados encadeados do utilizador (se existirem)
        user_data = validated_data.pop('user', {})
        user = instance.user  # Acede ao modelo User associado a este perfil

        # 2. Atualiza os campos do User (email, first_name, last_name)
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()  # Salva uma única vez fora do loop

        # 3. Atualiza os campos nativos do Profile (bio, avatar)
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
  old_password = serializers.CharField(
      required=True, write_only=True, style={'input_type': 'password'}
  )
  new_password = serializers.CharField(
      required=True, write_only=True, style={'input_type': 'password'}
  )

  def validate_old_password(self, value):
    request = self.context.get('request')
    if request and request.user:
      if not request.user.check_password(value):
        raise serializers.ValidationError('A senha atual está incorreta.')
    return value

  def validate_new_password(self, value):
    request = self.context.get('request')
    user = request.user if request else None
    # Valida regras padrão do Django (tamanho mínimo, senhas comuns, etc.)
    validate_password(value, user=user)
    return value

  def validate(self, attrs):
    if attrs.get('old_password') == attrs.get('new_password'):
      raise serializers.ValidationError({
          'new_password': 'A nova senha não pode ser igual à senha atual.'
      })
    return attrs