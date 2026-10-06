from rest_framework import serializers, status
from posts.models.post import Post
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
        return obj.likes.count()
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request:
            if request.user.is_authenticated:
                return obj.likes.filter(id=request.user.id).exists()

        return False

    def get_comments_count(self, obj):
        return obj.comments.count()
