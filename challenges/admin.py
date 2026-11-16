from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Challenge, Team, UserChallenge


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'points', 'point_type', 'requires_point', 'is_active', 'created_at')
    list_filter = ('category', 'difficulty', 'is_active')
    list_editable = ('is_active', 'requires_point', 'point_type')   # открыть/закрыть челлендж, нужна ли точка
    search_fields = ('title',)


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'status', 'ecopoint', 'proof_preview', 'points_awarded', 'taken_at')
    list_filter = ('status', 'challenge')
    search_fields = ('user__username', 'challenge__title')
    fields = ('user', 'challenge', 'status', 'admin_comment', 'ecopoint',
              'point_big', 'proof_big', 'proof_video_url', 'proof_comment',
              'points_awarded', 'taken_at', 'completed_at')
    readonly_fields = ('point_big', 'proof_big', 'points_awarded', 'completed_at', 'taken_at')
    actions = ['approve_selected', 'reject_selected']

    # большие превью «до / после»: открываются в новой вкладке, из админки выходить не нужно
    IMG = ('<a href="{0}" target="_blank" rel="noopener">'
           '<img src="{1}" style="max-height:320px;max-width:100%;border-radius:8px"></a>')

    @admin.display(description='Фото ДО (точка на карте)')
    def point_big(self, obj):
        if obj.ecopoint_id and obj.ecopoint.photo:
            return format_html(self.IMG, obj.ecopoint.photo.url, obj.ecopoint.photo.url)
        return '—'

    @admin.display(description='Фото ПОСЛЕ (доказательство)')
    def proof_big(self, obj):
        if obj.proof_photo:
            return format_html(self.IMG, obj.proof_photo.url, obj.proof_photo.url)
        return '—'

    @admin.display(description='Фото')
    def proof_preview(self, obj):
        if obj.proof_photo:
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" style="height:60px;border-radius:6px"></a>',
                obj.proof_photo.url,
            )
        return '—'

    @admin.action(description='✅ Одобрить выбранные (начислить баллы, точка станет зелёной)')
    def approve_selected(self, request, queryset):
        done = 0
        for uc in queryset.select_related('user', 'challenge', 'ecopoint'):
            problem = uc.approval_problem()
            if problem:
                self.message_user(request, f'Пропущено: {uc.user} — {uc.challenge}: {problem}.', messages.WARNING)
            elif uc.approve():
                done += 1
        if done:
            self.message_user(request, f'Одобрено: {done}', messages.SUCCESS)

    @admin.action(description='❌ Отклонить выбранные')
    def reject_selected(self, request, queryset):
        done = sum(1 for uc in queryset if uc.reject())
        self.message_user(request, f'Отклонено: {done}', messages.WARNING)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # если админ вручную выставил статус «Выполнено» в форме, баллы всё равно начислятся (один раз)
        if obj.status == 'completed' and not obj.points_awarded:
            obj.approve()


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('members',)
