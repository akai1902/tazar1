from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User

# Города и районные центры Кыргызстана: вместо свободного текста («бурмалдостан»)
CITY_CHOICES = [
    'Бишкек', 'Ош', 'Джалал-Абад', 'Каракол', 'Токмок', 'Нарын', 'Талас', 'Баткен',
    'Кант', 'Кара-Балта', 'Балыкчы', 'Чолпон-Ата', 'Узген', 'Кара-Куль', 'Майлуу-Суу',
    'Таш-Кумыр', 'Кызыл-Кыя', 'Сулюкта', 'Кемин', 'Орловка', 'Другой населённый пункт',
]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email')
    city = forms.ChoiceField(
        label='Город',
        choices=[('', '— выбери город —')] + [(c, c) for c in CITY_CHOICES],
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'city')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-input', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )
