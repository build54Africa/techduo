from django.core.management.base import BaseCommand
from core.models import Repository, PullRequest, FileChange, ConflictPrediction, Recommendation
from datetime import datetime


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        # Create sample repository
        repo, created = Repository.objects.get_or_create(
            name='mergesensei-demo',
            owner='techduo',
            defaults={
                'github_url': 'https://github.com/techduo/mergesensei-demo'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created repository'))
        
        # Create sample PRs
        pr1, created = PullRequest.objects.get_or_create(
            repository=repo,
            number=21,
            defaults={
                'title': 'Update dashboard UI',
                'author': 'alice',
                'base_branch': 'main',
                'head_branch': 'feature/dashboard-update',
                'status': 'open',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'github_url': 'https://github.com/techduo/mergesensei-demo/pull/21',
                'risk_score': 0.8,
                'conflict_files': ['src/dashboard.html'],
                'predicted_conflicts': [{'pr_number': 24, 'files': ['src/dashboard.html']}]
            }
        )
        
        pr2, created = PullRequest.objects.get_or_create(
            repository=repo,
            number=24,
            defaults={
                'title': 'Add new dashboard features',
                'author': 'bob',
                'base_branch': 'main',
                'head_branch': 'feature/dashboard-features',
                'status': 'open',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'github_url': 'https://github.com/techduo/mergesensei-demo/pull/24',
                'risk_score': 0.7,
                'conflict_files': ['src/dashboard.html'],
                'predicted_conflicts': [{'pr_number': 21, 'files': ['src/dashboard.html']}]
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created sample PRs'))
        
        # Create file changes
        FileChange.objects.get_or_create(
            pull_request=pr1,
            file_path='src/dashboard.html',
            defaults={
                'change_type': 'modified',
                'lines_added': 15,
                'lines_removed': 8
            }
        )
        
        FileChange.objects.get_or_create(
            pull_request=pr2,
            file_path='src/dashboard.html',
            defaults={
                'change_type': 'modified',
                'lines_added': 22,
                'lines_removed': 5
            }
        )
        
        # Create conflict prediction
        ConflictPrediction.objects.get_or_create(
            pull_request=pr1,
            conflicting_pr=pr2,
            defaults={
                'file_path': 'src/dashboard.html',
                'risk_level': 'high',
                'confidence_score': 0.85,
                'predicted_lines': [45, 46, 47, 48, 49]
            }
        )
        
        # Create recommendations
        Recommendation.objects.get_or_create(
            pull_request=pr1,
            recommendation_type='sync_suggestion',
            defaults={
                'title': 'Sync with PR #24 before merging',
                'description': 'Both PRs modify dashboard.html. Recommend syncing branches to avoid conflicts.',
                'priority': 'high',
                'ai_generated': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database with sample data'))
