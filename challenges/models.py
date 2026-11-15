from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone


class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Лёгкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]

    CATEGORY_CHOICES = [
        ('ecology', 'Экология'),
        ('culture', 'Культура'),
        ('volunteer', 'Волонтёрство'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='challenges/', blank=True, null=True)
    points = models.IntegerField(default=50)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    # NEW: админ может закрыть челлендж (он пропадёт из списка, взять его нельзя)
    is_active = models.BooleanField('Открыт', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Челлендж'
        verbose_name_plural = 'Челленджи'

    def __str__(self):
        return self.title


class UserChallenge(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В процессе'),
        ('pending', 'На проверке'),      # NEW: участник отправил доказательство
        ('completed', 'Выполнено'),
        ('rejected', 'Отклонено'),       # NEW: модератор отклонил, можно отправить заново
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    # доказательство
    proof_photo = models.ImageField('Фото-доказательство', upload_to='proofs/', blank=True, null=True)
    proof_video_url = models.URLField('Ссылка на видео', blank=True)
    proof_comment = models.TextField('Комментарий', blank=True)

    # какую проблему на карте решил участник (после одобрения точка станет зелёной)
    ecopoint = models.ForeignKey(
        'ecomap.EcoPoint', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='cleanups',
        verbose_name='Точка на карте',
    )

    admin_comment = models.CharField('Комментарий модератора', max_length=255, blank=True)
    points_awarded = models.BooleanField('Баллы начислены', default=False)
    taken_at = models.DateTimeField('Взят', default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-taken_at']
        verbose_name = 'Участие в челлендже'
        verbose_name_plural = 'Участия в челленджах'

    def __str__(self):
        return f"{self.user} — {self.challenge}"

    @transaction.atomic
    def approve(self):
        """Одобрить: баллы начисляются ОДИН раз, точка на карте становится «Решено»."""
        locked = UserChallenge.objects.select_for_update().get(pk=self.pk)
        if locked.points_awarded:
            return False

        now = timezone.now()
        locked.status = 'completed'
        locked.completed_at = now
        locked.points_awarded = True
        locked.save(update_fields=['status', 'completed_at', 'points_awarded'])

        get_user_model().objects.filter(pk=self.user_id).update(
            points=F('points') + self.challenge.points
        )
        if self.ecopoint_id:
            EcoPoint = apps.get_model('ecomap', 'EcoPoint')
            EcoPoint.objects.filter(pk=self.ecopoint_id).update(status='resolved')

        # держим объект в памяти актуальным
        self.status, self.completed_at, self.points_awarded = 'completed', now, True
        return True

    def reject(self, comment=''):
        if self.status == 'completed':
            return False
        self.status = 'rejected'
        self.admin_comment = comment or self.admin_comment or 'Доказательство не подошло. Попробуй ещё раз.'
        self.save(update_fields=['status', 'admin_comment'])
        return True


class Team(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='teams/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_teams')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams', blank=True)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def total_points(self):
        return sum(member.points for member in self.members.all())
