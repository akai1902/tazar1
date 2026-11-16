from django import forms
from django.core.files.uploadedfile import UploadedFile

from ecomap.models import EcoPoint
from .models import UserChallenge

MAX_UPLOAD = 5 * 1024 * 1024  # 5 МБ


class ProofForm(forms.ModelForm):
    """Форма «Отправить доказательство» на странице челленджа."""

    ecopoint = forms.ModelChoiceField(
        queryset=EcoPoint.objects.filter(status='active'),
        required=False,
        empty_label='— не привязывать к точке —',
        label='Какую проблему на карте ты решил?',
    )

    class Meta:
        model = UserChallenge
        fields = ['proof_photo', 'proof_video_url', 'proof_comment', 'ecopoint']
        labels = {
            'proof_photo': 'Фото-доказательство (до 5 МБ)',
            'proof_video_url': 'Ссылка на видео (необязательно)',
            'proof_comment': 'Комментарий (необязательно)',
        }
        widgets = {
            'proof_photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'proof_video_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'proof_comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Что ты сделал?'}),
        }

    def __init__(self, *args, challenge=None, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields['ecopoint']
        field.label_from_instance = lambda p: f'{p.title} ({p.get_type_display()})'

        # показываем только точки подходящего типа (река -> «Загрязнённая река» и т.д.)
        if challenge is not None and challenge.point_type:
            field.queryset = field.queryset.filter(type=challenge.point_type)

        # если челленджу нужна точка, без неё отправить доказательство нельзя
        if challenge is not None and challenge.requires_point:
            field.required = True
            field.empty_label = '— выбери точку —'
            field.label = 'Какую проблему на карте ты решил? (обязательно)'
            field.error_messages['required'] = (
                'Выбери точку на карте. Если подходящей нет, сначала отметь проблему на карте.'
            )

    def clean_proof_photo(self):
        photo = self.cleaned_data.get('proof_photo')
        if isinstance(photo, UploadedFile) and photo.size > MAX_UPLOAD:
            raise forms.ValidationError('Фото больше 5 МБ.')
        return photo

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('proof_photo') and not cleaned.get('proof_video_url'):
            raise forms.ValidationError('Прикрепи фото или ссылку на видео.')
        return cleaned
