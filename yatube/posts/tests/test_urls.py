from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    AUTHOR_NAME = 'author'
    ANOTHER_NAME = 'not_author'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.AUTHOR_NAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.select_related('author', 'group').create(
            text='Тестовое сообщение',
            author=cls.user,
            group=cls.group,
        )
        cls.available_urls = (
            '/',
            '/group/test-slug/',
            f'/profile/{cls.AUTHOR_NAME}/',
            f'/posts/{cls.post.id}/',
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{cls.AUTHOR_NAME}/': 'posts/profile.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/create/': 'posts/create.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create.html',
            '/unexisting_page/': 'core/404.html',
            '/follow/': 'posts/follow.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_user = User.objects.create_user(
            username=self.ANOTHER_NAME)
        self.another_client = Client()
        self.another_client.force_login(self.another_user)
        cache.clear()

    def test_pages_is_available_any_user(self):
        """Страницы доступны для любому пользователю
           /, /group/<slug>/, /profile/<username>/, /posts/<post_id>/
        """
        for url in self.available_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_page_authorized_user_create_post(self):
        """Страница /create/ доступна для авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_author_edit_post(self):
        """Страница /posts/<int:post_id>/edit/ доступна для автора"""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(
            self.post.author.get_username(),
            self.user.username)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_not_author_not_can_edit_post(self):
        """Страница /posts/<int:post_id>/edit/ не доступна
           для авторизованному пользователю НЕ автору"""
        response = self.another_client.get(f'/posts/{self.post.id}/edit/')
        self.assertNotEqual(
            self.post.author.get_username(),
            self.another_user.username)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unexisting_pages(self):
        """Страницы /unexisting_page/ (несуществующую страницу)
           для любому пользователю"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
