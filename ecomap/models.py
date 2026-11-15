from django.conf import settings
from django.db import models


class EcoPoint(models.Model):
    TYPE_CHOICES = [
        ('trash', 'Мусорная свалка'),
        ('water', 'Загрязнённая река'),
        ('forest', 'Вырубка леса'),
        ('air', 'Загрязнение воздуха'),
    ]

    STATUS_CHOICES = [
        ('active', 'Требует внимания'),
        ('resolved', 'Решено'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    photo = models.ImageField(upload_to='ecopoints/', blank=True, null=True)
    # NEW: видео вместо загрузки файла (файлы видео слишком тяжёлые для бесплатного хостинга)
    video_url = models.URLField('Ссылка на видео', blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Точка на карте'
        verbose_name_plural = 'Точки на карте'

    def __str__(self):
        return self.title
