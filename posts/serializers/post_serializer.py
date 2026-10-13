from rest_framework import serializers, status
from posts.models.post import Post
from posts.models.comment import Comment
from posts.serializers.comment_serializer import CommentSerializer


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author_username = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "created_at",
            "comments",
            "author_username",
            "comments_count",
            "likes_count",
            "is_liked",
        ]
        read_only_fields = ["author"]
    def get_likes_count(self, obj):
        return len(obj.likes.all())
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Verifica na lista prefetch sem executar SQL extra (.filter().exists())
            return request.user in obj.likes.all()
        return False

    def get_comments_count(self, obj):
        return Comment.objects.filter(post_id=obj.id).count()
