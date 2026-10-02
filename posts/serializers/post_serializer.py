from rest_framework import serializers
from posts.models.post import Post
from posts.serializers.comment_serializer import CommentSerializer


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "created_at",
            "comments",
        ]
        read_only_fields = ["author"]
