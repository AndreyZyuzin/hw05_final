from django.test import TestCase, Client
from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.urls = (
            '/about/author/',
            '/about/tech/',
        )
        cls.templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        """Проверка доступности адресов /about/* """
        for url in self.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_uses_correct_template(self):
        """Проверка шаблона для адреса /about/* """
        for template, url in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
