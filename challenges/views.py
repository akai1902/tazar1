from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from ecomap.models import EcoPoint

from .forms import ProofForm
from .models import Challenge, Team, UserChallenge

User = get_user_model()


# ───────────────────────── ЧЕЛЛЕНДЖИ ─────────────────────────

# участие, в котором человек ещё должен отправить доказательство
OPEN = ('in_progress', 'rejected')


def _point_from_request(request):
    """Точка, с которой пришёл участник (?point=ID). Только если она всё ещё открыта."""
    pid = request.POST.get('point') or request.GET.get('point') or ''
    if pid.isdigit():
        return EcoPoint.objects.filter(pk=pid, status='active').first()
    return None


def challenges_list(request):
    point = _point_from_request(request)
    challenges = Challenge.objects.filter(is_active=True)
    if point:
        # показываем только те челленджи, что подходят к типу выбранной точки
        challenges = challenges.filter(Q(point_type='') | Q(point_type=point.type))
    return render(request, 'challenges/list.html', {
        'challenges': challenges,
        'point': point,
        'total_challenges': Challenge.objects.filter(is_active=True).count(),
        # то, что отметили на карте, видно и здесь
        'open_points': EcoPoint.objects.filter(status='active').select_related('reported_by')[:6],
        'top_users': User.objects.order_by('-points', 'username')[:5],
        'users_count': User.objects.count(),
    })


def _detail_context(request, challenge, proof_form=None):
    user_challenge = None
    completed_count = pending_count = 0
    selected_point = _point_from_request(request)

    if request.user.is_authenticated:
        mine = UserChallenge.objects.filter(user=request.user, challenge=challenge)
        # текущее незавершённое участие (если есть); выполненные и «на проверке» не мешают взять снова
        user_challenge = mine.filter(status__in=OPEN).order_by('-taken_at').first()
        completed_count = mine.filter(status='completed').count()
        pending_count = mine.filter(status='pending').count()
        if proof_form is None and user_challenge:
            initial = {'ecopoint': selected_point.pk} if selected_point else None
            proof_form = ProofForm(challenge=challenge, initial=initial)

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
        'selected_point': selected_point,
        'completed_count': completed_count,
        'pending_count': pending_count,
    }


def challenge_detail(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    return render(request, 'challenges/detail.html', _detail_context(request, challenge))


@login_required
@require_POST
def take_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk, is_active=True)
    already = UserChallenge.objects.filter(
        user=request.user, challenge=challenge, status__in=OPEN
    ).exists()
    if already:
        messages.info(request, 'Ты уже выполняешь этот челлендж: отправь доказательство.')
    else:
        UserChallenge.objects.create(user=request.user, challenge=challenge)
        messages.success(request, 'Челлендж принят! Выполни задание и отправь доказательство.')

    url = reverse('challenge_detail', args=[pk])
    point = _point_from_request(request)
    if point:
        url += f'?point={point.pk}'
    return redirect(url)


@login_required
@require_POST
def submit_proof(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    uc = (UserChallenge.objects
          .filter(user=request.user, challenge=challenge, status__in=OPEN)
          .order_by('-taken_at').first())
    if uc is None:
        messages.error(request, 'Сначала прими челлендж.')
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
