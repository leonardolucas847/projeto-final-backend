
from rest_framework import viewsets, permissions
from posts.models import Post
from posts.serializers.post_serializer import PostSerializer
from .permissions import IsAuthorOrReadOnly
# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)