from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Имя пользователя',
            'email': 'Email',
        }
        help_texts = {
            'first_name': 'Заполните имя',
            'last_name': 'Заполните фамилию',
            'username': 'Требуется заполнить имя пользователя.',
            'email': 'Заполнить еmail',
        }
