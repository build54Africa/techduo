from rest_framework import serializers
from .models import Repository, PullRequest, FileChange, ConflictPrediction, Recommendation, MLModel


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = '__all__'


class FileChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChange
        fields = '__all__'


class PullRequestSerializer(serializers.ModelSerializer):
    file_changes = FileChangeSerializer(many=True, read_only=True)
    
    class Meta:
        model = PullRequest
        fields = '__all__'


class ConflictPredictionSerializer(serializers.ModelSerializer):
    pull_request = PullRequestSerializer(read_only=True)
    conflicting_pr = PullRequestSerializer(read_only=True)
    
    class Meta:
        model = ConflictPrediction
        fields = '__all__'


class RecommendationSerializer(serializers.ModelSerializer):
    pull_request = PullRequestSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = '__all__'


class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = '__all__'
