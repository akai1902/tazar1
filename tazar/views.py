from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import render

from challenges.models import Challenge, UserChallenge
from ecomap.models import EcoPoint


def home(request):
    popular = (
        Challenge.objects.filter(is_active=True)
        .annotate(taken=Count('userchallenge'))
        .order_by('-taken', '-created_at')[:3]
    )
    stats = {
        'users': get_user_model().objects.count(),
        'completed': UserChallenge.objects.filter(status='completed').count(),
        'points': EcoPoint.objects.count(),
        'resolved': EcoPoint.objects.filter(status='resolved').count(),
    }
    return render(request, 'home.html', {'popular_challenges': popular, 'stats': stats})
