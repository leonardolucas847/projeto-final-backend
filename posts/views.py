
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
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def feed(self, request):
        followed_users = request.user.profile.following.values_list(
            'user_id', flat=True
        )
        posts = self.get_queryset().filter(author_id__in=followed_users)

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated],)
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            is_liked = False
        else:
            post.likes.add(user)
            is_liked = True

        # RETORNA OS DADOS FRESCOS DIRETAMENTE NO POST (Evita precisar de um GET separado)
        return Response({
            'id': post.id,
            'likes_count': post.likes.count(),
            'is_liked': is_liked
        }, status=status.HTTP_200_OK)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        serializer.save(author=self.request.user, post_id=post_id)