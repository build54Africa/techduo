from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Repository, PullRequest, FileChange, ConflictPrediction, Recommendation, MLModel
from .serializers import (
    RepositorySerializer, PullRequestSerializer, FileChangeSerializer,
    ConflictPredictionSerializer, RecommendationSerializer
)
import json


# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'MergeSensei API',
        'version': '1.0.0'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_risk(request):
    """Analyze conflict risk for a pull request"""
    try:
        data = request.data
        pr_number = data.get('pr_number')
        repo_name = data.get('repo_name', 'mergesensei-demo')
        repo_owner = data.get('repo_owner', 'techduo')
        
        if not pr_number:
            return Response(
                {'error': 'pr_number is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create repository
        repo, created = Repository.objects.get_or_create(
            name=repo_name,
            owner=repo_owner,
            defaults={
                'github_url': f'https://github.com/{repo_owner}/{repo_name}'
            }
        )
        
        # Get or create pull request
        pr, created = PullRequest.objects.get_or_create(
            repository=repo,
            number=pr_number,
            defaults={
                'title': f'PR #{pr_number}',
                'author': 'unknown',
                'base_branch': 'main',
                'head_branch': f'feature-{pr_number}',
                'status': 'open',
                'created_at': '2024-01-15T10:00:00Z',
                'updated_at': '2024-01-15T10:00:00Z',
                'github_url': f'https://github.com/{repo_owner}/{repo_name}/pull/{pr_number}',
                'risk_score': 0.7,
                'conflict_files': ['src/dashboard.html'],
                'predicted_conflicts': []
            }
        )
        
        # Simple risk analysis logic
        risk_score = 0.7  # Mock value
        conflicts = []
        
        # Check for other open PRs that might conflict
        other_prs = PullRequest.objects.filter(
            repository=repo,
            status='open'
        ).exclude(number=pr_number)
        
        for other_pr in other_prs:
            # Simple conflict detection based on file overlap
            if 'dashboard.html' in pr.conflict_files and 'dashboard.html' in other_pr.conflict_files:
                conflicts.append({
                    'conflicting_pr_number': other_pr.number,
                    'conflicting_files': ['src/dashboard.html'],
                    'risk_level': 'high'
                })
        
        # Update PR with analysis results
        pr.risk_score = risk_score
        pr.predicted_conflicts = conflicts
        pr.save()
        
        result = {
            'pr_number': pr_number,
            'risk_score': risk_score,
            'conflicts': conflicts,
            'status': 'analyzed',
            'message': f'Risk analysis completed for PR #{pr_number}'
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_recommendation(request):
    """Get AI-powered recommendations for conflict resolution"""
    try:
        data = request.data
        pr_number = data.get('pr_number')
        conflicts = data.get('conflicts', [])
        
        if not pr_number:
            return Response(
                {'error': 'pr_number is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate mock recommendations based on conflicts
        recommendations = []
        
        if conflicts:
            for conflict in conflicts:
                recommendations.append({
                    'type': 'sync_suggestion',
                    'title': f'Sync with PR #{conflict.get("conflicting_pr_number")}',
                    'description': f'Both PRs modify the same files. Consider syncing branches before merging.',
                    'priority': conflict.get('risk_level', 'medium'),
                    'action': 'sync_branches'
                })
        
        # Add general recommendations
        recommendations.extend([
            {
                'type': 'review_suggestion',
                'title': 'Review conflicting files',
                'description': 'Carefully review all files that might have conflicts.',
                'priority': 'medium',
                'action': 'manual_review'
            },
            {
                'type': 'communication_suggestion',
                'title': 'Coordinate with team',
                'description': 'Communicate with other developers working on conflicting changes.',
                'priority': 'high',
                'action': 'team_communication'
            }
        ])
        
        result = {
            'pr_number': pr_number,
            'recommendations': recommendations,
            'priority': 'high' if conflicts else 'low',
            'ai_generated': True
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def predict_conflicts(request):
    """Predict conflicts using ML model (mock implementation)"""
    try:
        data = request.data
        features = data.get('features', {})
        
        # Mock ML prediction
        num_files = features.get('num_files_changed', 0)
        overlapping_files = features.get('overlapping_files', 0)
        
        # Simple rule-based prediction
        if overlapping_files > 0:
            risk_score = min(0.9, 0.3 + (overlapping_files * 0.2))
            prediction = 'high_risk' if risk_score > 0.7 else 'medium_risk'
        else:
            risk_score = 0.1
            prediction = 'low_risk'
        
        result = {
            'prediction': {
                'risk_score': risk_score,
                'prediction': prediction,
                'confidence': 0.85
            },
            'interpretation': {
                'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
                'interpretation': f'Predicted {prediction} based on {overlapping_files} overlapping files',
                'confidence': 0.85,
                'suggested_actions': [
                    'Review conflicting files' if overlapping_files > 0 else 'Proceed with merge',
                    'Coordinate with team',
                    'Plan merge strategy'
                ]
            },
            'model_info': {
                'version': '1.0',
                'type': 'Rule-based',
                'last_updated': '2024-01-15'
            }
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_pull_requests(request):
    """List all pull requests"""
    prs = PullRequest.objects.all()
    serializer = PullRequestSerializer(prs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_pull_request(request, pr_number):
    """Get specific pull request details"""
    try:
        pr = PullRequest.objects.get(number=pr_number)
        serializer = PullRequestSerializer(pr)
        return Response(serializer.data)
    except PullRequest.DoesNotExist:
        return Response(
            {'error': f'Pull request #{pr_number} not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
