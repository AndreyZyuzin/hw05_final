from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = '-- Группа не выбрана --'

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Сообщение',
            'group': 'Группа',
            'image': 'Картинка',
        }
        help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загрузите картинку',
        }
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'Напишите сообщение'}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Комментарий',
        }
        help_text = {
            'text': 'Введите текст комментария',
        }
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'Напишите комментарий'}
            ),
        }
