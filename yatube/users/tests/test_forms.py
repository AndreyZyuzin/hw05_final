from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from users.forms import CreationForm

User = get_user_model()


class UsersCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_labels_form(self):
        """labels в полях совпадает с ожидаемым."""
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Имя пользователя',
            'email': 'Email',
        }
        for field, desctiption in labels.items():
            with self.subTest(field=field):
                self.assertEqual(self.form.fields[field].label, desctiption)

    def test_help_texts_form(self):
        """help_texts в полях совпадает с ожидаемым."""
        help_texts = {
            'first_name': 'Заполните имя',
            'last_name': 'Заполните фамилию',
            'username': 'Требуется заполнить имя пользователя.',
            'email': 'Заполнить еmail',
        }
        for field, desctiption in help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(self.form.fields[field].help_text,
                                 desctiption)

    def test_create_user(self):
        """При отправке валидной формы со страницы reverse('users:signup')
           создаётся нового пользователя в базе данных"""
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'Ivan',
            'email': 'ivan@test.com',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.last().first_name, 'Иван')
        self.assertEqual(User.objects.last().last_name, 'Иванов')
        self.assertEqual(User.objects.last().username, 'Ivan')
        self.assertEqual(User.objects.last().email, 'ivan@test.com')
