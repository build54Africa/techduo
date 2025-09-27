from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.
class Repository(models.Model):
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    github_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner}/{self.name}"

    class Meta:
        verbose_name_plural = "Repositories"


class PullRequest(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='pull_requests')
    number = models.IntegerField()
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255)
    base_branch = models.CharField(max_length=255)
    head_branch = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='open')  # open, closed, merged
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    github_url = models.URLField()
    
    # Conflict prediction data
    risk_score = models.FloatField(default=0.0)
    conflict_files = models.JSONField(default=list)
    predicted_conflicts = models.JSONField(default=list)
    
    def __str__(self):
        return f"PR #{self.number}: {self.title}"

    class Meta:
        unique_together = ['repository', 'number']


class FileChange(models.Model):
    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='file_changes')
    file_path = models.CharField(max_length=500)
    change_type = models.CharField(max_length=20)  # added, modified, deleted
    lines_added = models.IntegerField(default=0)
    lines_removed = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.file_path} ({self.change_type})"


class ConflictPrediction(models.Model):
    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='conflict_predictions')
    conflicting_pr = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='conflicts_with')
    file_path = models.CharField(max_length=500)
    risk_level = models.CharField(max_length=20)  # low, medium, high
    confidence_score = models.FloatField()
    predicted_lines = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Conflict: PR #{self.pull_request.number} vs PR #{self.conflicting_pr.number}"


class Recommendation(models.Model):
    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=50)  # merge_strategy, sync_suggestion, etc.
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, default='medium')  # low, medium, high
    ai_generated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recommendation for PR #{self.pull_request.number}: {self.title}"


class MLModel(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    model_file = models.FileField(upload_to='models/', null=True, blank=True)
    accuracy_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} v{self.version}"