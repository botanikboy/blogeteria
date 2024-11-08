from datetime import timedelta
from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from blog.models import Category, Comment, Post

User = get_user_model()


class TestContent(TestCase):
    COMMENTED_POST = 0
    TEST_COMMENTS_COUNT = 5
    UNPUBLISHED_POST = 2
    PUBLISHED_IN_FUTURE_POST = 4

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.category = Category.objects.create(
            title='title', description='desc', slug='slug'
        )
        cls.posts = Post.objects.bulk_create(
            Post(
                title=f'title {index}', text='text',
                author=cls.author, category=cls.category,
                pub_date=timezone.now() - timedelta(days=index)
            ) for index in range(settings.POSTS_ON_PAGE + 3)
        )
        cls.posts[cls.UNPUBLISHED_POST].is_published = False
        cls.posts[cls.UNPUBLISHED_POST].save()
        cls.posts[cls.PUBLISHED_IN_FUTURE_POST].pub_date = (
            timezone.now() + timedelta(days=1))
        cls.posts[cls.PUBLISHED_IN_FUTURE_POST].save()

        cls.comments = Comment.objects.bulk_create(
            Comment(
                text=f'text comment {index}',
                author=cls.author,
                post=cls.posts[cls.COMMENTED_POST]
            ) for index in range(cls.TEST_COMMENTS_COUNT)
        )
        for delta, comment in enumerate(cls.comments):
            comment.created_at = timezone.now() - timedelta(days=delta)

    def test_posts_count_pages(self):
        urls_kwargs = (
            ('blog:index', None),
            ('blog:category_posts', {'slug': self.category.slug}),
            ('users:profile', {'username': self.author.username}),
        )
        for name, kwargs in urls_kwargs:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                page = response.context.get('page_obj')
                self.assertEqual(len(page.object_list), settings.POSTS_ON_PAGE)

    def test_posts_order_on_main(self):
        url = reverse('blog:index')
        response = self.client.get(url)
        page = response.context.get('page_obj')
        timestamps = [post.pub_date for post in page.object_list]
        sorted_timestamps = sorted(timestamps, reverse=True)
        self.assertEqual(timestamps, sorted_timestamps)

    def test_comments_order_on_detail_page(self):
        url = reverse(
            'blog:post_detail',
            kwargs={'pk': self.posts[self.COMMENTED_POST].pk}
        )
        response = self.client.get(url)
        all_dates = [
            comment.created_at for comment in response.context.get(
                'post').comments.all()]
        sorted_dates = sorted(all_dates)
        self.assertEqual(all_dates, sorted_dates)

    def test_anonimous_user_has_no_comment_form(self):
        url = reverse(
            'blog:post_detail',
            kwargs={'pk': self.posts[self.COMMENTED_POST].pk}
        )
        response = self.client.get(url)
        context = response.context
        self.assertNotIn('form', context)

    def test_authorized_user_has_comment_form(self):
        url = reverse(
            'blog:post_detail',
            kwargs={'pk': self.posts[self.COMMENTED_POST].pk}
        )
        self.client.force_login(self.reader)
        response = self.client.get(url)
        context = response.context
        self.assertIn('form', context)

    def test_anonimous_user_dont_see_hiden_or_future_posts(self):
        url = reverse(
            'users:profile', kwargs={'username': self.author.username})
        response = self.client.get(url)
        object_list = response.context.get('page_obj').object_list
        with self.subTest('anon_cant_see_unpublished'):
            self.assertNotIn(
                self.posts[self.UNPUBLISHED_POST], object_list)
        with self.subTest('anon_cant_see_future'):
            self.assertNotIn(
                self.posts[self.PUBLISHED_IN_FUTURE_POST], object_list)

    def test_author_can_see_hiden_or_future_posts(self):
        url = reverse(
            'users:profile', kwargs={'username': self.author.username})
        self.client.force_login(self.author)
        response = self.client.get(url)
        object_list = response.context.get('page_obj').object_list
        with self.subTest('author_can_see_unpublished'):
            self.assertIn(
                self.posts[self.UNPUBLISHED_POST], object_list)
        with self.subTest('author_can_see_future'):
            self.assertIn(
                self.posts[self.PUBLISHED_IN_FUTURE_POST], object_list)

    def test_anonimous_user_no_hiden_or_future_post_page(self):
        names_kwargs = (
            ('unpublished', {'pk': self.posts[self.UNPUBLISHED_POST].pk}),
            ('future', {'pk': self.posts[self.PUBLISHED_IN_FUTURE_POST].pk}),
        )
        for name, kwargs in names_kwargs:
            with self.subTest(name):
                url = reverse('blog:post_detail', kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
