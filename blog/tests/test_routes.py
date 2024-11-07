from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from blog.models import Comment, Category, Post

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.category = Category.objects.create(
            title='title', description='desc', slug='slug'
        )
        cls.post = Post.objects.create(
            title='title', text='text',
            author=cls.author, category=cls.category)
        cls.comment = Comment.objects.create(
            text='text',
            author=cls.author,
            post=cls.post,
        )
        return super().setUpTestData()

    def test_pages_availibility(self):
        urls = (
            ('blog:index', None),
            ('blog:post_detail', {'pk': self.post.pk}),
            ('blog:category_posts', {'slug': self.category.slug}),
            ('login', None),
            ('logout', None),
            ('users:registration', None),
            ('password_reset', None),
            ('pages:rules', None),
            ('pages:about', None),
            ('users:profile', {'username': self.author.username}),
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availibility_for_edit_and_delete(self):
        urls = (
            ('blog:post_edit', {'pk': self.post.pk}),
            ('blog:post_delete', {'pk': self.post.pk}),
            ('blog:comment_edit', {'pk': self.comment.pk,
                                   'post_pk': self.comment.post.pk}),
            ('blog:comment_delete', {'pk': self.comment.pk,
                                     'post_pk': self.comment.post.pk}),
            ('users:profile_edit', {'pk': self.author.pk}),
        )
        self.client.force_login(self.author)
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        self.client.force_login(self.reader)
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                redirect_url = reverse(
                    'blog:post_detail', kwargs={'pk': self.post.pk})
                response = self.client.get(url)
                if name == 'users:profile_edit':
                    self.assertEqual(
                        response.status_code, HTTPStatus.FORBIDDEN)
                else:
                    self.assertRedirects(response, redirect_url)
