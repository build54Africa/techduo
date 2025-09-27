from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('risk/', views.analyze_risk, name='analyze_risk'),
    path('recommendation/', views.get_recommendation, name='get_recommendation'),
    path('predict/', views.predict_conflicts, name='predict_conflicts'),
    path('prs/', views.list_pull_requests, name='list_pull_requests'),
    path('prs/<int:pr_number>/', views.get_pull_request, name='get_pull_request'),
]
