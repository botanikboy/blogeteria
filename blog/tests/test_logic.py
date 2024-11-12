from datetime import timedelta
from http import HTTPStatus

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from blog.models import Category, Comment, Location, Post

User = get_user_model()


class TestCommentCreation(TestCase):
    COMMENT_TEXT = 'comment text'
    TEST_POSTS_COUNT = 3
    PUBLISHED_POST = 0
    UNPUBLISHED_POST = 1
    PUBLISHED_IN_FUTURE_POST = 2

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.reader)
        cls.form_data = {'text': cls.COMMENT_TEXT}
        cls.posts = Post.objects.bulk_create(
            Post(
                title=f'title {index}', text='text',
                author=cls.author,
                pub_date=timezone.now() - timedelta(days=index)
            ) for index in range(cls.TEST_POSTS_COUNT)
        )
        cls.posts[cls.UNPUBLISHED_POST].is_published = False
        cls.posts[cls.UNPUBLISHED_POST].save()
        cls.posts[cls.PUBLISHED_IN_FUTURE_POST].pub_date = (
            timezone.now() + timedelta(days=1))
        cls.posts[cls.PUBLISHED_IN_FUTURE_POST].save()
        cls.published_url = reverse(
            'blog:comment_create',
            args=(cls.posts[cls.PUBLISHED_POST].pk,)
        )
        cls.unpublished_url = reverse(
            'blog:comment_create',
            args=(cls.posts[cls.UNPUBLISHED_POST].pk,)
        )
        cls.future_post_url = reverse(
            'blog:comment_create',
            args=(cls.posts[cls.PUBLISHED_IN_FUTURE_POST].pk,)
        )

    def test_anon_cant_create_comment(self):
        self.client.post(self.published_url, self.form_data)
        comm_count = Comment.objects.count()
        self.assertEqual(comm_count, 0)

    def test_auth_user_can_create_comment(self):
        self.auth_client.post(self.published_url, self.form_data)
        comment = Comment.objects.get()
        self.assertEqual(comment.text, self.COMMENT_TEXT)
        self.assertEqual(comment.post, self.posts[self.PUBLISHED_POST])
        self.assertEqual(comment.author, self.reader)

    def test_auth_user_cant_create_comment_to_hidden_post(self):
        response = self.auth_client.post(self.unpublished_url, self.form_data)
        comm_count = Comment.objects.count()
        self.assertEqual(comm_count, 0)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_auth_user_cant_create_comment_to_future_post(self):
        response = self.auth_client.post(self.future_post_url, self.form_data)
        comm_count = Comment.objects.count()
        self.assertEqual(comm_count, 0)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestCommentEditDelete(TestCase):
    COMMENT_TEXT = 'comment text'
    NEW_COMMENT_TEXT = 'new comment text'
    TEST_POSTS_COUNT = 3
    PUBLISHED_POST = 0
    UNPUBLISHED_POST = 1
    PUBLISHED_IN_FUTURE_POST = 2

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.posts = Post.objects.bulk_create(
            Post(
                title=f'title {index}', text='text',
                author=cls.author,
                pub_date=timezone.now() - timedelta(days=index)
            ) for index in range(cls.TEST_POSTS_COUNT)
        )
        cls.posts[cls.UNPUBLISHED_POST].is_published = False
        cls.posts[cls.UNPUBLISHED_POST].save()
        cls.posts[cls.PUBLISHED_IN_FUTURE_POST].pub_date = (
            timezone.now() + timedelta(days=1))
        cls.posts[cls.PUBLISHED_IN_FUTURE_POST].save()

        cls.comments = Comment.objects.bulk_create(
            Comment(
                text=cls.COMMENT_TEXT,
                author=cls.author,
                post=cls.posts[index]
            ) for index in range(cls.TEST_POSTS_COUNT)
        )
        for delta, comment in enumerate(cls.comments):
            comment.created_at = timezone.now() - timedelta(days=delta)
        cls.auth_reader_client = Client()
        cls.auth_reader_client.force_login(cls.reader)
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.form_data = {'text': cls.NEW_COMMENT_TEXT}
        cls.redirect_url = reverse(
            'blog:post_detail',
            args=(cls.posts[cls.PUBLISHED_POST].pk,)
        )

    def get_url(self, index: int, operation: str):
        return reverse(
            f'blog:comment_{operation}',
            kwargs={
                'post_pk': self.posts[index].pk,
                'pk': self.comments[index].pk,
            }
        )

    def test_author_can_delete_comment(self):
        response = self.auth_author_client.delete(
            self.get_url(self.PUBLISHED_POST, 'delete')
        )
        self.assertRedirects(response, self.redirect_url)
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, self.TEST_POSTS_COUNT - 1)

    def test_not_author_cant_delete_comment(self):
        response = self.auth_reader_client.delete(
            self.get_url(self.PUBLISHED_POST, 'delete')
        )
        self.assertRedirects(response, self.redirect_url)
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, self.TEST_POSTS_COUNT)

    def test_author_can_edit_comment(self):
        response = self.auth_author_client.post(
            self.get_url(self.PUBLISHED_POST, 'edit'),
            self.form_data
        )
        self.assertRedirects(response, self.redirect_url)
        comment = self.comments[self.PUBLISHED_POST]
        comment.refresh_from_db()
        self.assertEqual(comment.text, self.NEW_COMMENT_TEXT)

    def test_not_author_cant_edit_comment(self):
        response = self.auth_reader_client.post(
            self.get_url(self.PUBLISHED_POST, 'edit'),
            self.form_data
        )
        self.assertRedirects(response, self.redirect_url)
        comment = self.comments[self.PUBLISHED_POST]
        comment.refresh_from_db()
        self.assertEqual(comment.text, self.COMMENT_TEXT)

    def test_noone_can_delete_comment_to_hidden(self):
        response = self.auth_author_client.delete(
            self.get_url(self.UNPUBLISHED_POST, 'delete'))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_noone_can_edit_comment_to_hidden(self):
        response = self.auth_author_client.post(
            self.get_url(self.UNPUBLISHED_POST, 'edit'),
            self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_noone_can_delete_comment_to_future(self):
        response = self.auth_author_client.delete(
            self.get_url(self.PUBLISHED_IN_FUTURE_POST, 'delete')
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_noone_can_edit_comment_to_future(self):
        response = self.auth_author_client.post(
            self.get_url(self.PUBLISHED_IN_FUTURE_POST, 'edit'),
            self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestPostCreate(TestCase):
    POST_TITLE = 'title'
    POST_TEXT = 'text'
    PUB_DATE_FUTURE = timezone.now() + timedelta(days=2)
    IMAGE = SimpleUploadedFile(
        name='test_img.jpg',
        content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00'
                b'\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00'
                b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
        content_type='image/jpeg'
    )

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.category = Category.objects.create(
            title='category1',
            description='desc',
            slug='slug',
            )
        cls.location = Location.objects.create(name='place')
        cls.form_data = {
            'title': cls.POST_TITLE,
            'text': cls.POST_TEXT,
            'pub_date': cls.PUB_DATE_FUTURE.strftime('%Y-%m-%dT%H:%M'),
            'category': cls.category.pk,
            'location': cls.location.pk,
            'image': cls.IMAGE,
        }

    def test_auth_user_can_create_post(self):
        response = self.auth_client.post(
            reverse('blog:post_create'), self.form_data)
        self.assertRedirects(
            response, reverse('users:profile', args=(self.author.username,)))
        post = Post.objects.get()
        self.assertEqual(post.title, self.POST_TITLE)
        self.assertEqual(post.text, self.POST_TEXT)
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.location, self.location)
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.is_published, True)
        self.assertEqual(post.pub_date.date(), self.PUB_DATE_FUTURE.date())
        self.assertEqual(post.image.read(), self.IMAGE.read())

    def test_anon_cant_create_post(self):
        self.client.post(reverse('blog:post_create'), self.form_data)
        posts_count = Post.objects.count()
        self.assertEqual(posts_count, 0)


class TestPostEditDelete(TestCase):
    POST_TITLE = 'title'
    POST_TEXT = 'text'
    PUB_DATE_PAST = timezone.now() - timedelta(days=1)
    PUB_DATE_FUTURE = timezone.now() + timedelta(days=1)
    NEW_POST_TITLE = 'new title'
    NEW_POST_TEXT = 'new text'
    NEW_PUB_DATE = timezone.now() + timedelta(days=10)

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='reader')
        cls.auth_reader_client = Client()
        cls.auth_reader_client.force_login(cls.reader)

        cls.category = Category.objects.create(
            title='category1',
            description='desc',
            slug='slug'
            )
        cls.location = Location.objects.create(name='place')
        cls.form_data = {
            'title': cls.NEW_POST_TITLE,
            'text': cls.NEW_POST_TEXT,
            'pub_date': cls.NEW_PUB_DATE.strftime('%Y-%m-%dT%H:%M'),
        }
        cls.post_published = Post.objects.create(
            title=cls.POST_TITLE,
            text=cls.POST_TEXT,
            author=cls.author,
            pub_date=cls.PUB_DATE_PAST
        )
        cls.post_future = Post.objects.create(
            title=cls.POST_TITLE,
            text=cls.POST_TEXT,
            author=cls.author,
            pub_date=cls.PUB_DATE_FUTURE
        )

    def test_author_can_delete_post(self):
        response = self.auth_author_client.delete(
            reverse('blog:post_delete', args=(self.post_published.pk,))
        )
        self.assertRedirects(response, reverse('blog:index'))
        posts_count = Post.objects.count()
        self.assertEqual(posts_count, 1)

    def test_reader_cant_delete_post(self):
        response = self.auth_reader_client.delete(
            reverse('blog:post_delete', args=(self.post_published.pk,))
        )
        self.assertRedirects(
            response,
            reverse('blog:post_detail', args=(self.post_published.pk,))
        )
        posts_count = Post.objects.count()
        self.assertEqual(posts_count, 2)

    def test_author_can_edit_post(self):
        response = self.auth_author_client.post(
            reverse('blog:post_edit', args=(self.post_future.pk,)),
            self.form_data
        )
        self.assertRedirects(
            response,
            reverse('blog:post_detail', args=(self.post_future.pk,))
        )
        self.post_future.refresh_from_db()
        self.assertEqual(self.post_future.title, self.NEW_POST_TITLE)
        self.assertEqual(self.post_future.text, self.NEW_POST_TEXT)
        self.assertEqual(
            self.post_future.pub_date.date(), self.NEW_PUB_DATE.date())

    def test_reader_cant_edit_post(self):
        response = self.auth_reader_client.post(
            reverse('blog:post_edit', args=(self.post_published.pk,)),
            self.form_data
        )
        self.assertRedirects(
            response,
            reverse('blog:post_detail', args=(self.post_published.pk,))
        )
        self.post_published.refresh_from_db()
        self.assertEqual(self.post_published.title, self.POST_TITLE)
        self.assertEqual(self.post_published.text, self.POST_TEXT)

    def test_author_cant_change_pub_date_if_date_passed(self):
        response = self.auth_author_client.post(
            reverse('blog:post_edit', args=(self.post_published.pk,)),
            self.form_data
        )
        self.assertRedirects(
            response,
            reverse('blog:post_detail', args=(self.post_published.pk,))
        )
        self.post_published.refresh_from_db()
        self.assertEqual(self.post_published.title, self.NEW_POST_TITLE)
        self.assertEqual(self.post_published.text, self.NEW_POST_TEXT)
        self.assertEqual(
            self.post_published.pub_date.date(), self.PUB_DATE_PAST.date())
