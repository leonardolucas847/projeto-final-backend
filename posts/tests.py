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
    def test_list_posts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_create_post_unauthenticated(self):
        response = self.client.post(self.url, data={'content': 'Teste não autenticado'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data={'content': 'Teste feitor com o user autenticado'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


