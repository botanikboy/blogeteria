from rest_framework import serializers

from blog.models import Category, Post, Comment


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'author',
            'location',
            'category',
            'image',
        )
        read_only_fields = ('author',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'title',
            'description',
            'slug'
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'created_at', 'post', 'is_edited')
        read_only_fields = ('author', 'post', 'created_at', 'is_edited')
