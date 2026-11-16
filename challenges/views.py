from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ecomap.models import EcoPoint

from .forms import ProofForm
from .models import Challenge, Team, UserChallenge

User = get_user_model()


# ───────────────────────── ЧЕЛЛЕНДЖИ ─────────────────────────

def challenges_list(request):
    challenges = Challenge.objects.filter(is_active=True)
    return render(request, 'challenges/list.html', {
        'challenges': challenges,
        # тот же источник данных, что и у страницы рейтинга, поэтому цифры совпадают
        'top_users': User.objects.order_by('-points', 'username')[:5],
        'users_count': User.objects.count(),
    })


def _detail_context(request, challenge, proof_form=None):
    user_challenge = None
    if request.user.is_authenticated:
        user_challenge = UserChallenge.objects.filter(
            user=request.user, challenge=challenge
        ).first()
        if proof_form is None and user_challenge and user_challenge.status in ('in_progress', 'rejected'):
            proof_form = ProofForm(challenge=challenge)
    # сколько сейчас подходящих открытых точек (для подсказки в форме)
    open_points = 0
    if proof_form:
        qs = EcoPoint.objects.filter(status='active')
        if challenge.point_type:
            qs = qs.filter(type=challenge.point_type)
        open_points = qs.count()
    return {
        'challenge': challenge,
        'user_challenge': user_challenge,
        'proof_form': proof_form,
        'open_points': open_points,
    }


def challenge_detail(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    return render(request, 'challenges/detail.html', _detail_context(request, challenge))


@login_required
@require_POST
def take_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk, is_active=True)
    _, created = UserChallenge.objects.get_or_create(user=request.user, challenge=challenge)
    if created:
        messages.success(request, 'Челлендж принят! Выполни задание и отправь доказательство.')
    return redirect('challenge_detail', pk=pk)


@login_required
@require_POST
def submit_proof(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    uc = get_object_or_404(UserChallenge, challenge=challenge, user=request.user)

    if uc.status not in ('in_progress', 'rejected'):
        messages.error(request, 'Это задание уже отправлено на проверку или выполнено.')
        return redirect('challenge_detail', pk=pk)

    form = ProofForm(request.POST, request.FILES, instance=uc, challenge=challenge)
    if form.is_valid():
        uc = form.save(commit=False)
        uc.status = 'pending'
        uc.admin_comment = ''
        uc.save()
        messages.success(request, 'Отправлено на проверку! Модератор скоро посмотрит.')
        return redirect('challenge_detail', pk=pk)

    # форма с ошибками: показываем ту же страницу и подсвечиваем, что не так
    return render(request, 'challenges/detail.html', _detail_context(request, challenge, proof_form=form))


# ───────────────────────── КОМАНДЫ ─────────────────────────

@login_required
def teams_list(request):
    q = request.GET.get('q', '').strip()
    teams = Team.objects.prefetch_related('members')
    if q:
        teams = teams.filter(name__icontains=q)
    return render(request, 'challenges/teams.html', {'teams': teams, 'q': q})


@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team.objects.prefetch_related('members'), pk=pk)
    return render(request, 'challenges/team_detail.html', {'team': team})


@login_required
def create_team(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return redirect('create_team')
        team = Team.objects.create(
            name=name,
            description=request.POST.get('description', '').strip(),
            created_by=request.user,
        )
        team.members.add(request.user)
        return redirect('team_detail', pk=team.pk)
    return render(request, 'challenges/create_team.html')


@login_required
@require_POST
def join_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    team.members.add(request.user)
    messages.success(request, f'Вы вступили в команду «{team.name}».')
    return redirect('team_detail', pk=team.pk)


@login_required
@require_POST
def leave_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if team.created_by_id == request.user.id:
        messages.error(request, 'Создатель не может покинуть команду. Её можно только удалить.')
        return redirect('team_detail', pk=team.pk)
    team.members.remove(request.user)
    return redirect('teams')          # БЫЛО 'teams_list', такого имени нет → 500 ошибка


@login_required
@require_POST
def delete_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if team.created_by_id == request.user.id:
        team.delete()
        messages.success(request, 'Команда удалена.')
    return redirect('teams')


@login_required
def add_member(request, pk):
    team = get_object_or_404(Team, pk=pk, created_by=request.user)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        try:
            user = User.objects.get(username=username)
            team.members.add(user)
            messages.success(request, f'✅ {username} добавлен в команду!')
        except User.DoesNotExist:
            messages.error(request, f'❌ Пользователь "{username}" не найден!')
    return redirect('team_detail', pk=team.pk)


@login_required
@require_POST
def remove_member(request, pk, user_pk):
    team = get_object_or_404(Team, pk=pk, created_by=request.user)
    user = get_object_or_404(User, pk=user_pk)
    if user != team.created_by:
        team.members.remove(user)
    return redirect('team_detail', pk=team.pk)
