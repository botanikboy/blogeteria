from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class TestRoutes(TestCase):

    def test_index_page(self):
        '''index page availible for anonimous user'''
        url = reverse('blog:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
