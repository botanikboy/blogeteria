from rest_framework import serializers

from blog.models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

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
