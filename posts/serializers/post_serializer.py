from rest_framework import serializers
from posts.models.post import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "created_at",
        ]
        read_only_fields = ["author"]
