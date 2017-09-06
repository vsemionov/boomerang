import urllib

from django.urls import reverse
from rest_framework.test import APITestCase, RequestsClient
from rest_framework import status


class TestApiRoot(APITestCase):

    url = reverse('api-root')

    def test_allows_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_get(self):
        response = RequestsClient().options('http://testserver' + self.url)
        self.assertEqual(response.headers['Allow'], 'GET, HEAD, OPTIONS')

    def test_post_fails(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_fails(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_fails(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_fails(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_has_users_link(self):
        data = self.client.get(self.url).data
        self.assertEqual(urllib.parse.urlparse(data['users']).path, reverse('user-list'))

    def test_has_info_link(self):
        data = self.client.get(self.url).data
        self.assertEqual(urllib.parse.urlparse(data['info']).path, reverse('info-list'))

    def test_has_jwt_link(self):
        data = self.client.get(self.url).data
        self.assertEqual(urllib.parse.urlparse(data['jwt']).path, reverse('jwt-list'))

    def test_cors_allowed(self):
        response = RequestsClient().options('http://testserver' + self.url, headers={'Origin': 'http://localhost:8080'})
        self.assertTrue('Access-Control-Allow-Origin' in response.headers)
