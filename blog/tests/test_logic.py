from datetime import timedelta
from http import HTTPStatus

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from blog.models import Comment, Post

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

    def get_url(self, index: int, method: str):
        return reverse(
            f'blog:comment_{method}',
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
