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
from .ai_integration import ConflictPredictionAI, RecommendationAI, MLModelService
import json
from datetime import datetime


# Create your views here.

# Initialize AI services
conflict_ai = ConflictPredictionAI()
recommendation_ai = RecommendationAI()
ml_service = MLModelService()


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'MergeSensei API',
        'version': '1.0.0',
        'ai_available': conflict_ai.is_available()
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_risk(request):
    """Analyze conflict risk for a pull request using AI"""
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
                'risk_score': 0.0,
                'conflict_files': [],
                'predicted_conflicts': []
            }
        )
        
        # Get other open PRs for context
        other_prs = PullRequest.objects.filter(
            repository=repo,
            status='open'
        ).exclude(number=pr_number)
        
        # Prepare data for AI analysis
        pr_data = {
            'number': pr_number,
            'title': pr.title,
            'author': pr.author,
            'base_branch': pr.base_branch,
            'head_branch': pr.head_branch,
            'conflict_files': pr.conflict_files,
            'lines_added': sum(fc.lines_added for fc in pr.file_changes.all()),
            'lines_removed': sum(fc.lines_removed for fc in pr.file_changes.all()),
            'other_open_prs': [
                {
                    'number': other_pr.number,
                    'title': other_pr.title,
                    'conflict_files': other_pr.conflict_files
                }
                for other_pr in other_prs
            ]
        }
        
        # Use AI for conflict analysis
        ai_analysis = conflict_ai.analyze_conflict_risk(pr_data)
        
        # Update PR with AI analysis results
        pr.risk_score = ai_analysis['risk_score']
        pr.predicted_conflicts = ai_analysis.get('conflict_scenarios', [])
        pr.save()
        
        # Check for conflicts with other PRs
        conflicts = []
        for other_pr in other_prs:
            # Check for file overlap
            common_files = set(pr.conflict_files) & set(other_pr.conflict_files)
            if common_files:
                conflicts.append({
                    'conflicting_pr_number': other_pr.number,
                    'conflicting_files': list(common_files),
                    'risk_level': ai_analysis['risk_level'],
                    'ai_analysis': ai_analysis
                })
        
        result = {
            'pr_number': pr_number,
            'risk_score': ai_analysis['risk_score'],
            'risk_level': ai_analysis['risk_level'],
            'confidence': ai_analysis['confidence'],
            'conflicts': conflicts,
            'ai_analysis': ai_analysis,
            'status': 'analyzed',
            'message': f'AI-powered risk analysis completed for PR #{pr_number}',
            'ai_model': ai_analysis.get('ai_model', 'unknown')
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
        
        # Get PR data
        try:
            pr = PullRequest.objects.get(number=pr_number)
        except PullRequest.DoesNotExist:
            return Response(
                {'error': f'Pull request #{pr_number} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare data for AI recommendations
        pr_data = {
            'number': pr_number,
            'title': pr.title,
            'author': pr.author,
            'conflict_files': pr.conflict_files,
            'risk_level': 'high' if pr.risk_score > 0.7 else 'medium' if pr.risk_score > 0.4 else 'low'
        }
        
        # Generate AI recommendations
        ai_recommendations = recommendation_ai.generate_recommendations(pr_data, conflicts)
        
        # Save recommendations to database
        saved_recommendations = []
        for rec in ai_recommendations:
            recommendation, created = Recommendation.objects.get_or_create(
                pull_request=pr,
                recommendation_type=rec['type'],
                title=rec['title'],
                defaults={
                    'description': rec['description'],
                    'priority': rec['priority'],
                    'ai_generated': True
                }
            )
            saved_recommendations.append({
                'id': recommendation.id,
                'type': rec['type'],
                'title': rec['title'],
                'description': rec['description'],
                'priority': rec['priority'],
                'action': rec.get('action', 'manual_review'),
                'ai_generated': True
            })
        
        result = {
            'pr_number': pr_number,
            'recommendations': saved_recommendations,
            'priority': 'high' if conflicts else 'low',
            'ai_generated': True,
            'total_recommendations': len(saved_recommendations)
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
    """Predict conflicts using ML model and AI"""
    try:
        data = request.data
        features = data.get('features', {})
        
        # Use ML model if available
        ml_prediction = ml_service.predict_conflict(features)
        
        # Use AI for additional analysis
        pr_data = {
            'number': features.get('pr_number', 'unknown'),
            'title': features.get('title', 'Unknown PR'),
            'author': features.get('author', 'unknown'),
            'conflict_files': features.get('conflict_files', []),
            'lines_added': features.get('lines_added', 0),
            'lines_removed': features.get('lines_removed', 0),
            'other_open_prs': features.get('other_open_prs', [])
        }
        
        ai_analysis = conflict_ai.analyze_conflict_risk(pr_data)
        
        # Combine ML and AI predictions
        combined_risk_score = (
            ml_prediction.get('conflict_probability', 0.5) * 0.6 +
            ai_analysis['risk_score'] * 0.4
        )
        
        if combined_risk_score > 0.7:
            prediction = 'high_risk'
        elif combined_risk_score > 0.4:
            prediction = 'medium_risk'
        else:
            prediction = 'low_risk'
        
        result = {
            'prediction': {
                'risk_score': combined_risk_score,
                'prediction': prediction,
                'confidence': max(
                    ml_prediction.get('confidence', 0.5),
                    ai_analysis['confidence']
                )
            },
            'interpretation': {
                'risk_level': ai_analysis['risk_level'],
                'interpretation': f'Combined ML+AI prediction: {prediction}',
                'confidence': max(
                    ml_prediction.get('confidence', 0.5),
                    ai_analysis['confidence']
                ),
                'suggested_actions': ai_analysis.get('recommendations', [])
            },
            'model_info': {
                'ml_model': ml_prediction.get('model_type', 'not_trained'),
                'ai_model': ai_analysis.get('ai_model', 'unknown'),
                'version': '2.0',
                'type': 'Hybrid ML+AI',
                'last_updated': datetime.now().isoformat()
            },
            'ai_analysis': ai_analysis,
            'ml_prediction': ml_prediction
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def train_ml_model(request):
    """Train ML model on historical data"""
    try:
        # Get training data from database
        training_data = []
        
        # Get historical PRs with conflict information
        prs = PullRequest.objects.all()
        for pr in prs:
            # Create training sample
            sample = {
                'num_files_changed': len(pr.conflict_files),
                'lines_added': sum(fc.lines_added for fc in pr.file_changes.all()),
                'lines_removed': sum(fc.lines_removed for fc in pr.file_changes.all()),
                'has_conflicting_files': len(pr.conflict_files) > 0,
                'num_conflicting_prs': len(pr.predicted_conflicts),
                'overlapping_files': len(pr.conflict_files),
                'conflict_occurred': pr.risk_score > 0.5  # Simple heuristic
            }
            training_data.append(sample)
        
        if len(training_data) < 10:
            return Response(
                {'error': 'Not enough training data. Need at least 10 samples.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Train model
        training_result = ml_service.train_model(training_data)
        
        return Response(training_result, status=status.HTTP_200_OK)
        
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


@api_view(['GET'])
@permission_classes([AllowAny])
def ai_status(request):
    """Get AI service status"""
    return Response({
        'conflict_ai_available': conflict_ai.is_available(),
        'recommendation_ai_available': recommendation_ai.is_available(),
        'ml_model_trained': ml_service.is_trained,
        'openrouter_available': bool(conflict_ai.openrouter_api_key),
        'cohere_available': bool(conflict_ai.cohere_api_key)
    })