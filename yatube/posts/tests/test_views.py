import tempfile
import shutil
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Group, Post, Comment, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    AUTHOR_NAME = 'auth'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.AUTHOR_NAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.group_another = Group.objects.create(
            title='Тестовая другая группа',
            slug='test-another',
            description='Тестовое описание другой'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.posts = Post.objects.select_related('author', 'group')
        for i in range(1, 13):
            cls.posts.create(
                text=f'Тестовое сообщение {i}',
                author=cls.user,
                group=cls.group,
            )
        cls.post = cls.posts.create(
            text='Тестовое последнее сообщение',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.select_related('author', 'post').create(
            text='Тестовый коментарий',
            post=cls.post,
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile', kwargs={'username': self.AUTHOR_NAME}):
                'posts/profile.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:post_create'): 'posts/create.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон posts:index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('title'),
                         'Последние обновления на сайте')
        test_post = response.context.get('page_obj').object_list[0]
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.image, self.post.image)

    def test_profile_pages_show_correct_context(self):
        """Шаблон posts:profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.AUTHOR_NAME}))
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(response.context.get('author').username,
                         self.user.username)
        test_post = response.context.get('page_obj').object_list[0]
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.image, self.post.image)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон posts:group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.context.get('group'), self.group)
        self.assertEqual(response.context.get('group').title,
                         self.group.title)
        self.assertEqual(response.context.get('group').slug,
                         self.group.slug)
        self.assertEqual(response.context.get('group').description,
                         self.group.description)
        test_post = response.context.get('page_obj').object_list[0]
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.image, self.post.image)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон posts:post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}))

        test_post = response.context.get('post')
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.image, self.post.image)

        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

        comment = response.context.get('comments').first()
        self.assertEqual(comment, self.comment)
        self.assertEqual(comment.text, self.comment.text)
        self.assertEqual(comment.post, self.comment.post)
        self.assertEqual(comment.author, self.comment.author)

    def test_create_post_pages_show_correct_context(self):
        """Шаблон posts:post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_pages_show_correct_context(self):
        """Шаблон posts:post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('is_edit'), True)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_paginator_on_pages(self):
        """Пагинатор страницы правильно работают"""
        pages_names = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.AUTHOR_NAME}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        )
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_create_post_with_group(self):
        """Проверка, что при создании поста указать группу,
           то этот пост появляется"""
        post = Post.objects.select_related('author', 'group').create(
            text='Тестовое сообщение',
            author=self.user,
            group=self.group,
        )
        pages_names = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.AUTHOR_NAME}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        )
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertIn(post, response.context['page_obj'])

        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_another.slug}))
        self.assertNotIn(post, response.context['page_obj'])

    def test_cache_index_page(self):
        """Проверка работы кэша записей index.html"""
        reverse_name = reverse('posts:index')
        response = self.authorized_client.get(reverse_name)
        content = response.content
        Post.objects.create(
            text="Новое тестовое сообщение",
            author=self.user,
        )
        response = self.authorized_client.get(reverse_name)
        content_old = response.content
        self.assertEqual(content_old, content)

        cache.clear()
        response = self.authorized_client.get(reverse_name)
        content_new = response.content
        self.assertNotEqual(content_old, content_new)


class FollowTests(TestCase):
    AUTHOR_NAME = 'author'
    AUTHOR_2_NAME = 'author_2'
    USER_NAME = 'follower'
    USER_2_NAME = 'follower_2'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=cls.AUTHOR_NAME)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.author_2 = User.objects.create_user(username=cls.AUTHOR_2_NAME)
        cls.author_2_client = Client()
        cls.author_2_client.force_login(cls.author_2)
        cls.posts = Post.objects.select_related('author', 'group')
        cls.posts.create(
            text='Тестовое сообщение 1',
            author=cls.author,
        )
        cls.posts.create(
            text='Тестовое сообщение 2',
            author=cls.author,
        )
        cls.posts.create(
            text='Тестовое сообщение 3',
            author=cls.author_2
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=self.USER_NAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_2 = User.objects.create_user(username=self.USER_2_NAME)
        self.second_client = Client()
        self.second_client.force_login(self.user_2)
        self.follow_1 = Follow.objects.create(
            author=self.author,
            user=self.user,
        )
        self.follow_2 = Follow.objects.create(
            author=self.author_2,
            user=self.user_2,
        )

    def test_authorized_user_can_follow_other_users(self):
        """Авторизованный пользователь может подписываться
           на других пользователей."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.AUTHOR_2_NAME}))
        self.assertFalse(response.context.get('following'))

        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.AUTHOR_2_NAME})
        )
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.AUTHOR_2_NAME}))
        self.assertTrue(response.context.get('following'))

    def test_authorized_user_can_remove_follow(self):
        """Авторизованный пользователь может отписываться
           от других пользователей."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.AUTHOR_NAME}))
        self.assertTrue(response.context.get('following'))

        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.AUTHOR_NAME})
        )
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.AUTHOR_NAME}))
        self.assertFalse(response.context.get('following'))

    def test_new_post_appears_in_desired_feed(self):
        """Новая запись пользователя появляется в ленте тех, кто
           на него подписан и не появляется в ленте тех, кто не подписан."""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts_user_count = len(response.context['page_obj'])
        self.assertEqual(posts_user_count, 2)

        response = self.second_client.get(reverse('posts:follow_index'))
        posts_user_2_count = len(response.context['page_obj'])
        self.assertEqual(posts_user_2_count, 1)

        Post.objects.create(
            text='Тестовое сообщение 4',
            author=self.author,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']),
                         posts_user_count + 1)

        response = self.second_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']),
                         posts_user_2_count)
