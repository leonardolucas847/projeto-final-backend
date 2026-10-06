from django.db.models.fields import return_None
from rest_framework import viewsets, permissions, filters
from posts.models import Post, Comment
from posts.serializers.post_serializer import PostSerializer
from .serializers.comment_serializer import CommentSerializer
from .permissions import IsAuthorOrReadOnly
from posts.pagination import PostPagination
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response


# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-id').select_related('author').prefetch_related('likes', 'comments__author')
    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = '__all__'
    ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated],)
    def me(self, request):
        posts = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            return Response({'detail': 'Curtida removida.'}, status=status.HTTP_200_OK)
        post.likes.add(user)
        return Response({'detail': 'Post curtido com sucesso.'}, status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        serializer.save(author=self.request.user, post_id=post_id)