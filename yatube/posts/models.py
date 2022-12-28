from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Заголовок группы',

    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='Slug',
        help_text='Уникальная строка-индификатор',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание группы',

    )

    def __str__(self):
        return self.title


class Post(models.Model):

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата, когда был создан пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор, создавший пост',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Картинка',
        help_text='Загрузите картинку',
    )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    class Meta:
        ordering = ['-created']
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        help_text='Пост, для которого коментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор, создавший комментарий',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата, когда был создан комментарий',
    )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        help_text='Подписчик, который подписывается на автора',
        related_name='follower'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор, на которого подписываются',
        related_name='following'
    )

    def __str__(self):
        return f'{self.author} <- {self.user}'
