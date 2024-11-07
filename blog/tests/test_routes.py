from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from blog.models import Category, Post
from users.models import CustomUser


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = CustomUser.objects.create(username='author')
        cls.category = Category.objects.create(
            title='title', description='desc', slug='slug'
        )
        cls.post = Post.objects.create(
            title='title', text='text',
            author=cls.author, category=cls.category)
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
        )
        for name, kwargs in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
