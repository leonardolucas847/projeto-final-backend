
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

# Create your tests here.

class AccountAPITestCase(APITestCase):

    def setUp(self):
        self.user1 =User.objects.create_user(username='testRegistro2', email='test@registro2.com', password='registro1234')
        self.token_url = reverse('token_obtain_pair')
        self.profile_url = reverse('me')
        self.register_url = reverse('register')

    def test_register_user_success(self):
        data = {'username': 'testRegistro', 'email': 'test@registro.com', 'password': 'registro123'}
        response = self.client.post('/api/accounts/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        user = User.objects.get(username='testRegistro')
        self.assertTrue(user.check_password('registro123'))
    def test_login_user(self):
        response = self.client.post(self.token_url, {'username': 'testRegistro2', 'password': 'registro1234'})
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