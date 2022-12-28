from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.follower = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            text='Тест коммента',
            post=cls.post,
            author=cls.user,
        )
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.follower,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        props = {
            'post': 'text',
            'group': 'title',
            'comment': 'text',
        }
        for table, property in props.items():
            with self.subTest(table=table):
                t = self.__getattribute__(table)
                self.assertEqual(t.__getattribute__(property), str(t))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

        group = PostModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Slug',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата создания'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    expected_value
                )

        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'pub_date': 'Дата, когда был создан пост',
            'author': 'Автор, создавший пост',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

        group = PostModelTest.group
        field_help_texts = {
            'title': 'Заголовок группы',
            'slug': 'Уникальная строка-индификатор',
            'description': 'Описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

        field_help_texts = {
            'post': 'Пост, для которого коментарий',
            'author': 'Автор, создавший комментарий',
            'text': 'Введите текст комментария',
            'created': 'Дата, когда был создан комментарий',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).help_text,
                    expected_value
                )

        field_help_texts = {
            'user': 'Подписчик, который подписывается на автора',
            'author': 'Автор, на которого подписываются',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).help_text,
                    expected_value
                )
