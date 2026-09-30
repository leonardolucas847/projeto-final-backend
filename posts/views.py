
from rest_framework import viewsets, permissions, filters
from posts.models import Post
from posts.serializers.post_serializer import PostSerializer
from .permissions import IsAuthorOrReadOnly
from posts.pagination import StandardResultsSetPagination
# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-id')
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = '__all__'
    ordering = ['-id']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)