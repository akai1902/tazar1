from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm, LoginForm


from challenges.models import Team
teams = sorted(Team.objects.prefetch_related('members'),
               key=lambda t: t.total_points(), reverse=True)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
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
    from django.contrib.auth import get_user_model

    User = get_user_model()
    users = User.objects.order_by('-points', 'username')
    return render(request, 'accounts/leaderboard.html', {'users': users, 'teams': teams})
