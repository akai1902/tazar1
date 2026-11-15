from django.urls import path
from . import views

urlpatterns = [
    path('challenges/', views.challenges_list, name='challenges'),
    path('challenges/<int:pk>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:pk>/take/', views.take_challenge, name='take_challenge'),
    path('challenges/<int:pk>/submit/', views.submit_proof, name='submit_proof'),
    path('teams/', views.teams_list, name='teams'),
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),
    path('teams/create/', views.create_team, name='create_team'),
    path('teams/<int:pk>/join/', views.join_team, name='join_team'),
    path('teams/<int:pk>/leave/', views.leave_team, name='leave_team'),
    path('teams/<int:pk>/delete/', views.delete_team, name='delete_team'),
    path('teams/<int:pk>/add-member/', views.add_member, name='add_member'),
    path('teams/<int:pk>/remove-member/<int:user_pk>/', views.remove_member, name='remove_member'),
]
