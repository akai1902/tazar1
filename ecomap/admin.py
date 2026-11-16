from django.contrib import admin, messages
from django.utils.html import format_html

from .models import EcoPoint


@admin.register(EcoPoint)
class EcoPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'reported_by', 'created_at')
    list_filter = ('type', 'status')
    search_fields = ('title', 'description', 'reported_by__username')
    actions = ['mark_resolved', 'mark_active']
    exclude = ('photo',)              # убираем стандартную ссылку «Currently», из которой нельзя выйти
    readonly_fields = ('photo_big',)

    @admin.display(description='Фото')
    def photo_big(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{0}" target="_blank" rel="noopener">'
                '<img src="{0}" style="max-height:320px;max-width:100%;border-radius:8px"></a>',
                obj.photo.url)
        return '—'

    @admin.action(description='🟢 Отметить как «Решено»')
    def mark_resolved(self, request, queryset):
        n = queryset.update(status='resolved')
        self.message_user(request, f'Обновлено: {n}', messages.SUCCESS)

    @admin.action(description='⚠️ Вернуть «Требует внимания»')
    def mark_active(self, request, queryset):
        n = queryset.update(status='active')
        self.message_user(request, f'Обновлено: {n}', messages.SUCCESS)
