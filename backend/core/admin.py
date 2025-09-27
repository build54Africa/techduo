from django.contrib import admin
from .models import Repository, PullRequest, FileChange, ConflictPrediction, Recommendation, MLModel


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    search_fields = ['name', 'owner']


@admin.register(PullRequest)
class PullRequestAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'author', 'status', 'risk_score', 'created_at']
    list_filter = ['status', 'risk_score']
    search_fields = ['title', 'author', 'number']


@admin.register(FileChange)
class FileChangeAdmin(admin.ModelAdmin):
    list_display = ['file_path', 'change_type', 'lines_added', 'lines_removed']
    list_filter = ['change_type']


@admin.register(ConflictPrediction)
class ConflictPredictionAdmin(admin.ModelAdmin):
    list_display = ['pull_request', 'conflicting_pr', 'risk_level', 'confidence_score']
    list_filter = ['risk_level']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recommendation_type', 'priority', 'ai_generated']
    list_filter = ['recommendation_type', 'priority', 'ai_generated']


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'accuracy_score', 'is_active']
    list_filter = ['is_active']
