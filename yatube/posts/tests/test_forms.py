import tempfile
import shutil
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    AUTHOR_NAME = 'Author'

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=self.AUTHOR_NAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_author_create_post(self):
        """При отправке валидной формы со страницы создания поста
        reverse('posts:post_create') создаётся новая запись в базе данных"""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовое сообщение',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.last()
        self.assertEqual(post.text, 'Тестовое сообщение')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, 'posts/small.gif')

    def test_author_edit_group_and_text_of_self_post(self):
        """При отправке валидной формы со страницы редактирования поста
        reverse('posts:post_edit') происходит изменение поста с post_id
        в базе данных"""
        post = Post.objects.select_related('author', 'group').create(
            text='Тестовое сообщение',
            author=self.user,
            group=self.group,
        )
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2'
        )
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        reverse_name = reverse('posts:post_edit',
                               kwargs={'post_id': post.id})

        response = self.authorized_client.get(reverse_name)

        form_data = {
            'text': 'Обновленное сообщение',
            'group': group2.id,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        post = Post.objects.last()
        self.assertEqual(post.text, 'Обновленное сообщение')
        self.assertEqual(post.group, group2)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image, 'posts/small2.gif')
        self.assertFalse(Post.objects.filter(
            group=self.group, id=post.id).exists())

    def test_after_successfull_send_comment_on_page_of_post(self):
        """Проверка, что после успешной отправки комментарий
           появляется на странице поста"""
        post = Post.objects.select_related('author', 'group').create(
            text='Тестовое сообщение',
            author=self.user,
        )
        reverse_name = reverse('posts:add_comment',
                               kwargs={'post_id': post.id})

        form_data = {
            'text': 'Тестовой коментарий',
        }

        response = self.authorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.last()
        self.assertEqual(comment.text, 'Тестовой коментарий')
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.author, self.user)

    def test_only_authorized_user_can_comment_on_post(self):
        """Проверка комментировать посты может только
           авторизованный пользователь"""
        post = Post.objects.select_related('author', 'group').create(
            text='Тестовое сообщение',
            author=self.user,
        )
        reverse_name = reverse('posts:add_comment',
                               kwargs={'post_id': post.id})

        response = self.authorized_client.post(
            reverse_name,
            data={'text': 'Комментарий авторизированного пользователя'},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), 1)

        response = self.guest_client.post(
            reverse_name,
            data={'text': 'Комментарий гостевого пользователя'},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), 1)
