from rest_framework import serializers
from posts.models.post import Post
from posts.serializers.comment_serializer import CommentSerializer


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author_username = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "created_at",
            "comments",
            "author_username",
        ]
        read_only_fields = ["author"]
