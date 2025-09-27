from django.urls import path
from . import views, github_views

urlpatterns = [
    # Existing API endpoints
    path('health/', views.health_check, name='health_check'),
    path('risk/', views.analyze_risk, name='analyze_risk'),
    path('recommendation/', views.get_recommendation, name='get_recommendation'),
    path('predict/', views.predict_conflicts, name='predict_conflicts'),
    path('train/', views.train_ml_model, name='train_ml_model'),
    path('ai-status/', views.ai_status, name='ai_status'),
    path('prs/', views.list_pull_requests, name='list_pull_requests'),
    path('prs/<int:pr_number>/', views.get_pull_request, name='get_pull_request'),
    
    # GitHub integration endpoints
    path('github/status/', github_views.github_status, name='github_status'),
    path('github/connect/', github_views.connect_repository, name='connect_repository'),
    path('github/sync/', github_views.sync_pull_requests, name='sync_pull_requests'),
    path('github/analyze/', github_views.analyze_github_pr, name='analyze_github_pr'),
    path('github/search/', github_views.search_repositories, name='search_repositories'),
    path('github/repo-prs/', github_views.repo_prs, name='github_repo_prs'),
]