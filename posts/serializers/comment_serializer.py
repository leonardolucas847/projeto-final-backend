from rest_framework import serializers
from posts.models.comment import Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'author',
            'author_id',
            'author_username',
            'content',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['author', 'author_id', 'author_username', 'post']