from rest_framework import serializers
from posts.models.post import Post
from posts.serializers.comment_serializer import CommentSerializer


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    author_username = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'author_id',
            'author_username',
            'content',
            'created_at',
            'comments',
            'comments_count',
            'likes_count',
            'is_liked',
        ]
        read_only_fields = ['author', 'author_id', 'author_username']

    def get_likes_count(self, obj):
        return len(obj.likes.all())

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False

    def get_comments_count(self, obj):
        # Utiliza a relação já carregada na memória (prefetch) sem executar query N+1 extra no banco
        return len(obj.comments.all())