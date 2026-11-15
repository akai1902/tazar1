from django.contrib import admin, messages

from .models import EcoPoint


@admin.register(EcoPoint)
class EcoPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'reported_by', 'created_at')
    list_filter = ('type', 'status')
    search_fields = ('title', 'description', 'reported_by__username')
    actions = ['mark_resolved', 'mark_active']

    @admin.action(description='🟢 Отметить как «Решено»')
    def mark_resolved(self, request, queryset):
        n = queryset.update(status='resolved')
        self.message_user(request, f'Обновлено: {n}', messages.SUCCESS)

    @admin.action(description='⚠️ Вернуть «Требует внимания»')
    def mark_active(self, request, queryset):
        n = queryset.update(status='active')
        self.message_user(request, f'Обновлено: {n}', messages.SUCCESS)
