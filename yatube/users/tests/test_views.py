from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

User = get_user_model()


class UsersPagesViewsTests(TestCase):
    def setUp(self):
        # Создаем неавторизованый клиент
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        """Шаблон users:signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
