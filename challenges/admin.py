from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Challenge, Team, UserChallenge


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'points', 'is_active', 'created_at')
    list_filter = ('category', 'difficulty', 'is_active')
    list_editable = ('is_active',)          # открыть/закрыть челлендж одним кликом
    search_fields = ('title',)


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'status', 'ecopoint', 'proof_preview', 'points_awarded', 'taken_at')
    list_filter = ('status', 'challenge')
    search_fields = ('user__username', 'challenge__title')
    readonly_fields = ('proof_preview', 'points_awarded', 'completed_at', 'taken_at')
    actions = ['approve_selected', 'reject_selected']

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
        done = sum(1 for uc in queryset.select_related('user', 'challenge') if uc.approve())
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
