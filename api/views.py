from rest_framework.exceptions import NotFound
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from blog.models import Post, Category, Comment

from .permissions import IsAuthor
from .serializers import CategorySerializer, PostSerializer, CommentSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthor,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentVeiwSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthor,)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        self._validate_post(post_id)
        return Comment.objects.filter(post=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        self._validate_post(post_id)
        serializer.save(
            author=self.request.user,
            post_id=post_id
        )

    def perform_update(self, serializer):
        post_id = self.kwargs.get('post_id')
        self._validate_post(post_id)
        serializer.save(
            author=self.request.user,
            post_id=post_id,
            is_edited=True
        )

    def _validate_post(self, post_id):
        if not Post.objects.filter(pk=post_id):
            raise NotFound('No such post.')
