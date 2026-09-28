from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from .models import Post
from django.contrib.auth.models import User


# Create your tests here.

class PostAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse('post-list')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        self.post = Post.objects.create(author=self.user, content='Post original do testuser')
        self.detail_url = reverse('post-detail', kwargs={'pk': self.post.pk})
    def test_list_posts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_create_post_unauthenticated(self):
        response = self.client.post(self.url, data={'content': 'Teste não autenticado'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data={'content': 'Teste feitor com o user autenticado'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_update_post_by_author(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.detail_url, data={'content': 'mudando coteudo como autor'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_update_post_by_non_author(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(self.detail_url, data={'content': 'mudando coteudo como um não autor'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_obtain_jwt_token(self):
        response = self.client.post(reverse('token_obtain_pair'), data={'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)




