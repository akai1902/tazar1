from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import EcoPoint

MAX_UPLOAD = 5 * 1024 * 1024  # 5 МБ


class EcoPointForm(forms.ModelForm):
    """Форма добавления точки на карту (приходит с карты через fetch + FormData)."""

    class Meta:
        model = EcoPoint
        fields = ['title', 'description', 'type', 'photo', 'video_url', 'latitude', 'longitude']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'type': 'Тип проблемы',
            'photo': 'Фото',
            'video_url': 'Ссылка на видео',
            'latitude': 'Широта',
            'longitude': 'Долгота',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # фото «ДО» обязательно: по нему понятно, что нужно сделать на месте
        self.fields['photo'].required = True
        self.fields['photo'].error_messages['required'] = 'Прикрепи фото проблемы.'

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 3:
            raise forms.ValidationError('Слишком короткое название (минимум 3 символа).')
        return title

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if isinstance(photo, UploadedFile) and photo.size > MAX_UPLOAD:
            raise forms.ValidationError('Фото больше 5 МБ.')
        return photo

    def clean_latitude(self):
        value = self.cleaned_data['latitude']
        if not -90 <= value <= 90:
            raise forms.ValidationError('Широта должна быть от -90 до 90.')
        return value

    def clean_longitude(self):
        value = self.cleaned_data['longitude']
        if not -180 <= value <= 180:
            raise forms.ValidationError('Долгота должна быть от -180 до 180.')
        return value
