from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from blog.models import Category, Post

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.category = Category.objects.create(
            title='title', description='desc', slug='slug'
        )
        Post.objects.bulk_create(
            Post(
                title=f'title {index}', text='text',
                author=cls.author, category=cls.category,
                pub_date=timezone.now() - timedelta(days=index)
            ) for index in range(settings.POSTS_ON_PAGE + 2)
        )

    def test_posts_count_on_main(self):
        url = reverse('blog:index')
        response = self.client.get(url)
        page = response.context.get('page_obj')
        print(page.object_list)
        self.assertEqual(len(page.object_list), settings.POSTS_ON_PAGE)

    def test_posts_order_on_main(self):
        url = reverse('blog:index')
        response = self.client.get(url)
        page = response.context.get('page_obj')
        timestamps = [post.pub_date for post in page.object_list]
        sorted_timestamps = sorted(timestamps, reverse=True)
        self.assertEqual(timestamps, sorted_timestamps)
