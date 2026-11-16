from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, RegisterForm


def _next_url(request):
    """Куда вернуть после входа (?next=...). Только на наш же сайт."""
    url = request.POST.get('next') or request.GET.get('next') or ''
    if url and url_has_allowed_host_and_scheme(
        url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return url
    return None


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(_next_url(request) or 'home')
        messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # раньше всегда кидало на главную, теперь возвращает туда, откуда пришёл
                return redirect(_next_url(request) or 'home')
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    from challenges.models import UserChallenge
    from ecomap.models import EcoPoint

    user_challenges = UserChallenge.objects.filter(user=request.user)
    user_points = EcoPoint.objects.filter(reported_by=request.user)

    return render(request, 'accounts/profile.html', {
        'user_challenges': user_challenges,
        'user_points': user_points,
    })


def leaderboard_view(request):
    from challenges.models import Team

    users = get_user_model().objects.order_by('-points', 'username')
    teams = sorted(
        Team.objects.prefetch_related('members'),
        key=lambda t: t.total_points(),
        reverse=True,
    )
    return render(request, 'accounts/leaderboard.html', {'users': users, 'teams': teams})
