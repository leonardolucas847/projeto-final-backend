from rest_framework import serializers

from posts.models.comment import Comment

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author','author_username', 'content', 'created_at', 'updated_at')
        read_only_fields = ["author", "post"]