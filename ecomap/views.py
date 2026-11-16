from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import EcoPointForm
from .models import EcoPoint

DAILY_LIMIT = 10  # точек в сутки на одного пользователя (защита от мусора)


def _error(message, status=400):
    return JsonResponse({'status': 'error', 'message': message}, status=status)


def ecomap_view(request):
    user = request.user
    points_data = []
    for p in EcoPoint.objects.select_related('reported_by'):
        points_data.append({
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'type': p.type,
            'status': p.status,
            'lat': p.latitude,
            'lng': p.longitude,
            'reported_by': p.reported_by.username,
            'photo': p.photo.url if p.photo else '',
            'video_url': p.video_url,
            'can_delete': user.is_authenticated and (user.is_staff or p.reported_by_id == user.id),
        })
    # в шаблоне: {{ points|json_script:"points-data" }}, это безопасно для любого текста
    return render(request, 'ecomap/map.html', {'points': points_data})


@require_POST
def add_point(request):
    if not request.user.is_authenticated:
        return _error('Нужно войти в аккаунт.', status=401)

    if not request.user.is_staff:
        recent = EcoPoint.objects.filter(
            reported_by=request.user, created_at__gte=timezone.now() - timedelta(days=1)
        ).count()
        if recent >= DAILY_LIMIT:
            return _error(f'Лимит: не больше {DAILY_LIMIT} точек в сутки.', status=429)

    form = EcoPointForm(request.POST, request.FILES)
    if not form.is_valid():
        parts = []
        for name, errors in form.errors.items():
            label = form.fields[name].label or name
            parts.append(f'{label}: {errors[0]}')
        return _error('; '.join(parts))

    point = form.save(commit=False)
    point.reported_by = request.user
    point.save()
    return JsonResponse({'status': 'ok', 'id': point.pk})


@require_POST
def delete_point(request, pk):
    if not request.user.is_authenticated:
        return _error('Нужно войти в аккаунт.', status=401)

    point = get_object_or_404(EcoPoint, pk=pk)
    if not (request.user.is_staff or point.reported_by_id == request.user.id):
        return _error('Можно удалять только свои точки.', status=403)

    point.delete()
    return JsonResponse({'status': 'ok'})
