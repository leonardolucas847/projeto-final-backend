from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from .models import Post, Comment
from django.contrib.auth.models import User


# Create your tests here.

class PostAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse('post-list')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        self.post = Post.objects.create(author=self.user, content='Post original do testuser')
        self.post2 = Post.objects.create(author=self.user, content='apredendo react')
        self.post3 = Post.objects.create(author=self.user, content='usando o DRF')
        self.comment = Comment.objects.create(post=self.post, author=self.user, content='comentario inicial do teste')
        self.comment2 = Comment.objects.create(post=self.post, author=self.user, content='comentario 2 inicial do teste')

        self.detail_url = reverse('post-detail', kwargs={'pk': self.post.pk})
    def test_list_posts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
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


    def test_search_posts (self):
        response = self.client.get(self.url, {'search': 'DRF'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_ordering_posts(self):
        response = self.client.get(self.url, {'ordering': 'id'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.post.id)

    def test_get_post_detail_with_comments(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 2)
    def test_like_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        like_url = reverse('post-like', kwargs={'pk': self.post.pk})
        response = self.client.post(like_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Post curtido com sucesso.')
    def test_like_post_unauthenticated(self):
        like_url = reverse('post-like', kwargs={'pk': self.post.pk})
        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_like_toggle_post(self):
        self.client.force_authenticate(user=self.user)
        like_url = reverse('post-like', kwargs={'pk': self.post.pk})

        response = self.client.post(like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Post curtido com sucesso.')
        self.assertTrue(self.post.likes.filter(id=self.user.id).exists())
        response2 = self.client.post(like_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['detail'], 'Curtida removida.')
        self.assertFalse(self.post.likes.filter(id=self.user.id).exists())

    def test_get_my_posts_authenticated(self):
        self.client.force_authenticate(user=self.user)
        posts_url = reverse('post-me')
        response = self.client.get(posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        for post_data in response.data['results']:
            self.assertEqual(post_data["author_username"], self.user.username)
    def test_get_my_posts_unauthenticated(self):
        posts_url = reverse('post-me')
        response = self.client.get(posts_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class CommentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='user2', password='password123')
        self.post = Post.objects.create(author=self.user, content='post para teste')
        self.comment = Comment.objects.create(post=self.post, author=self.user , content='comentario inicial do teste')

        self.list_url = reverse('comment-list')
        self.detail_url = reverse(
            'comment-detail', kwargs={'pk': self.comment.pk}
        )
    def test_create_comment_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {'post': self.post.id, 'content': 'Novo comentário'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author_username'], self.user.username)

    def test_update_comment_by_non_author(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(
            self.detail_url, {'content': 'Tentando alterar'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

