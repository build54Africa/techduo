"""
GitHub integration views for MergeSensei
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .github_service import GitHubService
from .models import Repository, PullRequest, FileChange
from .ai_integration import ConflictPredictionAI, RecommendationAI
import logging

logger = logging.getLogger(__name__)

# Initialize services
github_service = GitHubService()
conflict_ai = ConflictPredictionAI()
recommendation_ai = RecommendationAI()


@api_view(['GET'])
@permission_classes([AllowAny])
def github_status(request):
    """Check GitHub service status"""
    return Response({
        'available': github_service.is_available(),
        'message': 'GitHub service is available' if github_service.is_available() else 'GitHub token not configured'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def connect_repository(request):
    """Connect to a GitHub repository"""
    try:
        data = request.data
        owner = data.get('owner')
        repo_name = data.get('repo_name')
        
        if not owner or not repo_name:
            return Response(
                {'error': 'owner and repo_name are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not github_service.is_available():
            return Response(
                {'error': 'GitHub service not available. Please configure GITHUB_TOKEN.'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Get repository info from GitHub
        repo_info = github_service.get_repository_info(owner, repo_name)
        
        # Create or update repository in database
        repository, created = Repository.objects.get_or_create(
            name=repo_name,
            owner=owner,
            defaults={
                'github_url': repo_info['html_url']
            }
        )
        
        if not created:
            repository.github_url = repo_info['html_url']
            repository.save()
        
        return Response({
            'repository': {
                'id': repository.id,
                'name': repository.name,
                'owner': repository.owner,
                'github_url': repository.github_url,
                'created': created
            },
            'github_info': repo_info,
            'message': f'Successfully connected to {owner}/{repo_name}'
        })
        
    except Exception as e:
        logger.error(f"Failed to connect repository: {e}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def sync_pull_requests(request):
    """Sync pull requests from GitHub repository"""
    try:
        data = request.data
        owner = data.get('owner')
        repo_name = data.get('repo_name')
        state = data.get('state', 'open')
        
        if not owner or not repo_name:
            return Response(
                {'error': 'owner and repo_name are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not github_service.is_available():
            return Response(
                {'error': 'GitHub service not available'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Get repository from database
        try:
            repository = Repository.objects.get(name=repo_name, owner=owner)
        except Repository.DoesNotExist:
            return Response(
                {'error': 'Repository not found. Please connect repository first.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Fetch PRs from GitHub
        github_prs = github_service.get_pull_requests(owner, repo_name, state)
        
        synced_prs = []
        for github_pr in github_prs:
            # Create or update PR in database
            pr, created = PullRequest.objects.get_or_create(
                repository=repository,
                number=github_pr['number'],
                defaults={
                    'title': github_pr['title'],
                    'author': github_pr['author'],
                    'base_branch': github_pr['base_branch'],
                    'head_branch': github_pr['head_branch'],
                    'status': github_pr['status'],
                    'created_at': github_pr['created_at'],
                    'updated_at': github_pr['updated_at'],
                    'github_url': github_pr['html_url'],
                    'risk_score': 0.0,
                    'conflict_files': [],
                    'predicted_conflicts': []
                }
            )
            
            if not created:
                # Update existing PR
                pr.title = github_pr['title']
                pr.author = github_pr['author']
                pr.status = github_pr['status']
                pr.updated_at = github_pr['updated_at']
                pr.save()
            
            # Create file changes
            FileChange.objects.filter(pull_request=pr).delete()  # Remove old file changes
            
            # Extract file information for conflict analysis
            conflict_files = []
            for file in github_pr.get('files', []):
                if file['status'] in ['added', 'modified']:
                    conflict_files.append(file['filename'])
                    
                    # Create file change record
                    FileChange.objects.create(
                        pull_request=pr,
                        file_path=file['filename'],
                        change_type=file['status'],
                        lines_added=file['additions'],
                        lines_removed=file['deletions']
                    )
            
            # Update PR with file information
            pr.conflict_files = conflict_files
            pr.save()
            
            synced_prs.append({
                'number': pr.number,
                'title': pr.title,
                'author': pr.author,
                'status': pr.status,
                'conflict_files': conflict_files,
                'created': created
            })
        
        return Response({
            'repository': f"{owner}/{repo_name}",
            'synced_prs': synced_prs,
            'total_synced': len(synced_prs),
            'message': f'Successfully synced {len(synced_prs)} pull requests'
        })
        
    except Exception as e:
        logger.error(f"Failed to sync pull requests: {e}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_github_pr(request):
    """Analyze a specific GitHub pull request"""
    try:
        data = request.data
        owner = data.get('owner')
        repo_name = data.get('repo_name')
        pr_number = data.get('pr_number')
        
        if not all([owner, repo_name, pr_number]):
            return Response(
                {'error': 'owner, repo_name, and pr_number are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not github_service.is_available():
            return Response(
                {'error': 'GitHub service not available'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Get detailed PR information from GitHub
        try:
            github_pr = github_service.get_pull_request_details(owner, repo_name, pr_number)
        except Exception as e:
            if "Not Found" in str(e):
                return Response(
                    {'error': f'Pull request #{pr_number} not found in {owner}/{repo_name}'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            elif "Forbidden" in str(e):
                return Response(
                    {'error': 'Access denied. Repository may be private or you may not have permission.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            else:
                raise e
        
        # Prepare data for AI analysis
        pr_data = {
            'number': pr_number,
            'title': github_pr['title'],
            'author': github_pr['author'],
            'base_branch': github_pr['base_branch'],
            'head_branch': github_pr['head_branch'],
            'conflict_files': [f['filename'] for f in github_pr['files'] if f['status'] in ['added', 'modified']],
            'lines_added': github_pr['additions'],
            'lines_removed': github_pr['deletions'],
            'other_open_prs': []  # We'll need to fetch this separately
        }
        
        # Use AI to analyze conflict risk
        ai_analysis = conflict_ai.analyze_conflict_risk(pr_data)
        
        # Get recommendations
        conflicts = ai_analysis.get('conflict_scenarios', [])
        recommendations = recommendation_ai.generate_recommendations(pr_data, conflicts)
        
        return Response({
            'pr_number': pr_number,
            'repository': f"{owner}/{repo_name}",
            'github_data': github_pr,
            'ai_analysis': ai_analysis,
            'recommendations': recommendations,
            'status': 'analyzed'
        })
        
    except Exception as e:
        logger.error(f"Failed to analyze GitHub PR: {e}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def search_repositories(request):
    """Search for GitHub repositories"""
    try:
        query = request.GET.get('q', '')
        language = request.GET.get('language')
        
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not github_service.is_available():
            return Response(
                {'error': 'GitHub service not available'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        repositories = github_service.search_repositories(query, language)
        
        return Response({
            'query': query,
            'language': language,
            'repositories': repositories,
            'total': len(repositories)
        })
        
    except Exception as e:
        logger.error(f"Failed to search repositories: {e}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
