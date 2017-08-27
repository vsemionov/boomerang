from django.test import TestCase
from django.urls import reverse
from rest_framework.test import RequestsClient


class TestApiRoot(TestCase):

    url = reverse('index')

    def test_allows_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertTrue(response.status_code < 400)

    def test_only_get(self):
        response = RequestsClient().options('http://testserver' + self.url)
        self.assertEqual(response.headers['Allow'], 'GET, HEAD, OPTIONS')

    def test_get_redirects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_post_redirects(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_put_redirects(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 302)

    def test_patch_redirects(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, 302)

    def test_delete_redirects(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirect_location(self):
        response = RequestsClient().get('http://testserver' + self.url, allow_redirects=False)
        self.assertTrue(response.is_redirect)
        self.assertEqual(response.headers['Location'], reverse('api-root'))

#TODO: check cors
