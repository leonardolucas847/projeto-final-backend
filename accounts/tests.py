
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
import tempfile
from io import BytesIO
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile

# Create your tests here.

def generate_test_image():
  """Gera uma imagem temporária válida em memória para testes de upload."""
  file = BytesIO()
  image = Image.new('RGB', (100, 100), color='blue')
  image.save(file, 'jpeg')
  file.seek(0)
  return SimpleUploadedFile(
      'test_avatar.jpg', file.read(), content_type='image/jpeg'
  )

class AccountAPITestCase(APITestCase):

    def setUp(self):
        self.user_password = 'SenhaDoLogin123!'
        self.user1 =User.objects.create_user(username='testRegistro2', email='test@registro2.com', password=self.user_password)
        self.token_url = reverse('token_obtain_pair')
        self.profile_url = reverse('me')
        self.register_url = reverse('register')
        self.change_password_url = reverse('change_password')



    def test_register_user_success(self):
        data = {'username': 'testRegistro', 'email': 'test@registro.com', 'password': 'registro123'}
        response = self.client.post('/api/accounts/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        user = User.objects.get(username='testRegistro')
        self.assertTrue(user.check_password('registro123'))
    def test_login_user(self):
        response = self.client.post(self.token_url, {'username': 'testRegistro2', 'password': self.user_password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_profile_success(self):
        """Valida o acesso aos dados do perfil /me/ com token autenticado."""
        # Gera o token na memória sem precisar fazer requisição extra de HTTP
        refresh = RefreshToken.for_user(self.user1)
        access_token = str(refresh.access_token)


        # Injeta o cabeçalho Authorization: Bearer <token> no cliente de teste
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user1.username)
        self.assertEqual(response.data['email'], self.user1.email)

    def test_get_profile_unauthorized(self):
        """Garante que requisições sem o token na rota /me/ são bloqueadas com 401."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_success(self):
        """Valida a atualização parcial de dados do perfil via PATCH na rota /me/."""
        refresh = RefreshToken.for_user(self.user1)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        update_data = {
            'first_name': 'Desenvolvedor',
            'last_name': 'Python',
        }
        response = self.client.patch(self.profile_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Desenvolvedor')
        self.assertEqual(response.data['last_name'], 'Python')

        # Garante que o banco de dados foi atualizado
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Desenvolvedor')

    def test_obtain_token_invalid_password(self):
        login_data = {
            'username': self.user1.username,
            'password': 'senha_completamente_errada',
        }
        response = self.client.post(self.token_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_obtain_token_nonexistent_user(self):
        login_data = {
            'username': 'fantasma_nao_existe',
            'password': 'qualquer_senha',
        }
        response = self.client.post(self.token_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_duplicate_username(self):
        """Garante que tentar cadastrar um username que já existe retorna 400 Bad Request."""
        data = {
            'username': self.user1.username,  # 'usuariocadastrado' já criado no setUp
            'email': 'novo_email@teste.com',
            'password': 'outra_senha123',
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_duplicate_email(self):
        data = {
            'username': 'novo usuario',
            'email': self.user1.email,
            'password': 'outra_senha123',
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_change_password_success(self):
        """Garante a troca de senha com sucesso e validação no banco."""
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
        )

        data = {
            'old_password': self.user_password,
            'new_password': 'NovaSenhaSegura123!',
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Confirma que a nova senha foi atualizada com sucesso no banco de dados
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.check_password('NovaSenhaSegura123!'))

    def test_change_password_wrong_old_password(self):
        """Garante que fornecer a senha atual incorreta retorna 400 Bad Request."""
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
        )

        data = {
            'old_password': 'senha_antiga_errada',
            'new_password': 'NovaSenhaSegura123!',
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthorized(self):
        """Garante que usuários não autenticados recebam 401 Unauthorized ao tentar alterar senha."""
        data = {
            'old_password': self.user_password,
            'new_password': 'NovaSenhaSegura123!',
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class FollowAndAvatarAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password123'
        )

        self.profile1, _ = Profile.objects.get_or_create(user=self.user1)
        self.profile2, _ = Profile.objects.get_or_create(user=self.user2)

        self.follow_url = reverse(
            'follow_toggle', kwargs={'user_id': self.user2.id}
        )
        self.self_follow_url = reverse(
            'follow_toggle', kwargs={'user_id': self.user1.id}
        )
        self.profile_url = reverse('me')

    def test_follow_user_success(self):
        """Garante que o usuário consegue seguir outro com sucesso."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.follow_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['detail'], f'Você agora está seguindo {self.user2.username}.'
        )
        self.assertTrue(self.profile1.following.filter(id=self.profile2.id).exists())

    def test_unfollow_user_toggle(self):
        """Garante que fazer POST novamente no mesmo usuário cancela o follow (unfollow)."""
        self.profile1.following.add(self.profile2)  # Já começa seguindo

        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.follow_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['detail'], f'Você deixou de seguir {self.user2.username}.'
        )
        self.assertFalse(
            self.profile1.following.filter(id=self.profile2.id).exists()
        )

    def test_follow_self_fails(self):
        """Garante que um usuário não consegue seguir a si mesmo."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.self_follow_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'], 'Você não pode seguir a si mesmo.'
        )

    def test_follow_unauthenticated_fails(self):
        """Garante que requisição não autenticada no follow é bloqueada (401)."""
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_upload_avatar_success(self):
        """Garante o envio e salvamento correto da imagem de perfil (avatar)."""
        self.client.force_authenticate(user=self.user1)
        test_image = generate_test_image()

        response = self.client.patch(
            self.profile_url, {'avatar': test_image}, format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile1.refresh_from_db()
        self.assertTrue(bool(self.profile1.avatar))