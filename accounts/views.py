from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Profile

from accounts.serializers.user_serializer import UserRegisterSerializer, User, UserProfileSerializer, ChangePasswordSerializer


# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
class ChangePasswordView(APIView):

  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    serializer = ChangePasswordSerializer(
        data=request.data, context={'request': request}
    )
    if serializer.is_valid():
      user = request.user
      user.set_password(serializer.validated_data['new_password'])
      user.save()
      return Response(
          {'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK
      )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FollowToggleView(APIView):
  """Permite que o usuário autenticado siga ou deixe de seguir outro usuário."""

  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if target_user == request.user:
      return Response(
          {'detail': 'Você não pode seguir a si mesmo.'},
          status=status.HTTP_400_BAD_REQUEST,
      )

    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    target_profile, _ = Profile.objects.get_or_create(user=target_user)

    if target_profile in user_profile.following.all():
      user_profile.following.remove(target_profile)
      return Response(
          {'detail': f'Você deixou de seguir {target_user.username}.'},
          status=status.HTTP_200_OK,
      )

    user_profile.following.add(target_profile)
    return Response(
        {'detail': f'Você agora está seguindo {target_user.username}.'},
        status=status.HTTP_200_OK,
    )