from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Repository, PullRequest, FileChange, ConflictPrediction, Recommendation, MLModel
import json
from datetime import datetime


class MergeSenseiAPITestCase(APITestCase):
    """Test cases for MergeSensei API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test repository
        self.repository = Repository.objects.create(
            name='mergesensei-demo',
            owner='techduo',
            github_url='https://github.com/techduo/mergesensei-demo'
        )
        
        # Create test pull requests
        self.pr1 = PullRequest.objects.create(
            repository=self.repository,
            number=21,
            title='Update dashboard UI',
            author='alice',
            base_branch='main',
            head_branch='feature/dashboard-update',
            status='open',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            github_url='https://github.com/techduo/mergesensei-demo/pull/21',
            risk_score=0.8,
            conflict_files=['src/dashboard.html'],
            predicted_conflicts=[{'pr_number': 24, 'files': ['src/dashboard.html']}]
        )
        
        self.pr2 = PullRequest.objects.create(
            repository=self.repository,
            number=24,
            title='Add new dashboard features',
            author='bob',
            base_branch='main',
            head_branch='feature/dashboard-features',
            status='open',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            github_url='https://github.com/techduo/mergesensei-demo/pull/24',
            risk_score=0.7,
            conflict_files=['src/dashboard.html'],
            predicted_conflicts=[{'pr_number': 21, 'files': ['src/dashboard.html']}]
        )
        
        # Create file changes
        self.file_change1 = FileChange.objects.create(
            pull_request=self.pr1,
            file_path='src/dashboard.html',
            change_type='modified',
            lines_added=15,
            lines_removed=8
        )
        
        self.file_change2 = FileChange.objects.create(
            pull_request=self.pr2,
            file_path='src/dashboard.html',
            change_type='modified',
            lines_added=22,
            lines_removed=5
        )
        
        # Create conflict prediction
        self.conflict_prediction = ConflictPrediction.objects.create(
            pull_request=self.pr1,
            conflicting_pr=self.pr2,
            file_path='src/dashboard.html',
            risk_level='high',
            confidence_score=0.85,
            predicted_lines=[45, 46, 47, 48, 49]
        )
        
        # Create recommendation
        self.recommendation = Recommendation.objects.create(
            pull_request=self.pr1,
            recommendation_type='sync_suggestion',
            title='Sync with PR #24 before merging',
            description='Both PRs modify dashboard.html. Recommend syncing branches to avoid conflicts.',
            priority='high',
            ai_generated=True
        )

    def test_health_check(self):
        """Test health check endpoint"""
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('service', response.data)
        self.assertIn('version', response.data)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['service'], 'MergeSensei API')

    def test_analyze_risk_success(self):
        """Test risk analysis endpoint with valid data"""
        url = reverse('analyze_risk')
        data = {
            'pr_number': 25,
            'repo_name': 'mergesensei-demo',
            'repo_owner': 'techduo'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pr_number', response.data)
        self.assertIn('risk_score', response.data)
        self.assertIn('conflicts', response.data)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['pr_number'], 25)
        self.assertEqual(response.data['status'], 'analyzed')

    def test_analyze_risk_missing_pr_number(self):
        """Test risk analysis endpoint with missing pr_number"""
        url = reverse('analyze_risk')
        data = {
            'repo_name': 'mergesensei-demo',
            'repo_owner': 'techduo'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'pr_number is required')

    def test_analyze_risk_existing_pr(self):
        """Test risk analysis with existing PR"""
        url = reverse('analyze_risk')
        data = {
            'pr_number': 21,
            'repo_name': 'mergesensei-demo',
            'repo_owner': 'techduo'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pr_number'], 21)
        # Should detect conflicts with PR #24
        self.assertTrue(len(response.data['conflicts']) > 0)

    def test_get_recommendation_success(self):
        """Test recommendation endpoint with valid data"""
        url = reverse('get_recommendation')
        data = {
            'pr_number': 21,
            'conflicts': [
                {
                    'conflicting_pr_number': 24,
                    'conflicting_files': ['src/dashboard.html'],
                    'risk_level': 'high'
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pr_number', response.data)
        self.assertIn('recommendations', response.data)
        self.assertIn('priority', response.data)
        self.assertIn('ai_generated', response.data)
        self.assertEqual(response.data['pr_number'], 21)
        self.assertTrue(response.data['ai_generated'])
        self.assertTrue(len(response.data['recommendations']) > 0)

    def test_get_recommendation_missing_pr_number(self):
        """Test recommendation endpoint with missing pr_number"""
        url = reverse('get_recommendation')
        data = {
            'conflicts': []
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'pr_number is required')

    def test_get_recommendation_no_conflicts(self):
        """Test recommendation endpoint with no conflicts"""
        url = reverse('get_recommendation')
        data = {
            'pr_number': 21,
            'conflicts': []
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['priority'], 'low')
        # Should still have general recommendations
        self.assertTrue(len(response.data['recommendations']) > 0)

    def test_predict_conflicts_success(self):
        """Test conflict prediction endpoint with valid features"""
        url = reverse('predict_conflicts')
        data = {
            'features': {
                'num_files_changed': 3,
                'overlapping_files': 2
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('prediction', response.data)
        self.assertIn('interpretation', response.data)
        self.assertIn('model_info', response.data)
        
        prediction = response.data['prediction']
        self.assertIn('risk_score', prediction)
        self.assertIn('prediction', prediction)
        self.assertIn('confidence', prediction)

    def test_predict_conflicts_high_risk(self):
        """Test conflict prediction with high risk scenario"""
        url = reverse('predict_conflicts')
        data = {
            'features': {
                'num_files_changed': 5,
                'overlapping_files': 3
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prediction = response.data['prediction']
        self.assertGreater(prediction['risk_score'], 0.7)
        self.assertEqual(prediction['prediction'], 'high_risk')

    def test_predict_conflicts_low_risk(self):
        """Test conflict prediction with low risk scenario"""
        url = reverse('predict_conflicts')
        data = {
            'features': {
                'num_files_changed': 2,
                'overlapping_files': 0
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prediction = response.data['prediction']
        self.assertLess(prediction['risk_score'], 0.4)
        self.assertEqual(prediction['prediction'], 'low_risk')

    def test_list_pull_requests(self):
        """Test listing all pull requests"""
        url = reverse('list_pull_requests')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)  # We created 2 PRs in setUp
        
        # Check that both PRs are in the response
        pr_numbers = [pr['number'] for pr in response.data]
        self.assertIn(21, pr_numbers)
        self.assertIn(24, pr_numbers)

    def test_get_pull_request_success(self):
        """Test getting specific pull request"""
        url = reverse('get_pull_request', kwargs={'pr_number': 21})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['number'], 21)
        self.assertEqual(response.data['title'], 'Update dashboard UI')
        self.assertEqual(response.data['author'], 'alice')

    def test_get_pull_request_not_found(self):
        """Test getting non-existent pull request"""
        url = reverse('get_pull_request', kwargs={'pr_number': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('not found', response.data['error'])

    def test_analyze_risk_creates_repository(self):
        """Test that analyze_risk creates repository if it doesn't exist"""
        url = reverse('analyze_risk')
        data = {
            'pr_number': 30,
            'repo_name': 'new-repo',
            'repo_owner': 'new-owner'
        }
        
        # Verify repository doesn't exist
        self.assertFalse(Repository.objects.filter(name='new-repo', owner='new-owner').exists())
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify repository was created
        self.assertTrue(Repository.objects.filter(name='new-repo', owner='new-owner').exists())

    def test_analyze_risk_creates_pull_request(self):
        """Test that analyze_risk creates pull request if it doesn't exist"""
        url = reverse('analyze_risk')
        data = {
            'pr_number': 30,
            'repo_name': 'mergesensei-demo',
            'repo_owner': 'techduo'
        }
        
        # Verify PR doesn't exist
        self.assertFalse(PullRequest.objects.filter(number=30).exists())
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify PR was created
        self.assertTrue(PullRequest.objects.filter(number=30).exists())

    def test_recommendation_types(self):
        """Test that recommendations include different types"""
        url = reverse('get_recommendation')
        data = {
            'pr_number': 21,
            'conflicts': [
                {
                    'conflicting_pr_number': 24,
                    'conflicting_files': ['src/dashboard.html'],
                    'risk_level': 'high'
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recommendations = response.data['recommendations']
        
        # Check for different recommendation types
        types = [rec['type'] for rec in recommendations]
        self.assertIn('sync_suggestion', types)
        self.assertIn('review_suggestion', types)
        self.assertIn('communication_suggestion', types)

    def test_predict_conflicts_edge_cases(self):
        """Test conflict prediction with edge cases"""
        url = reverse('predict_conflicts')
        
        # Test with no features
        data = {'features': {}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test with negative values
        data = {'features': {'num_files_changed': -1, 'overlapping_files': -1}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_error_handling(self):
        """Test API error handling for invalid data"""
        # Test with invalid JSON
        url = reverse('analyze_risk')
        response = self.client.post(
            url, 
            'invalid json', 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MergeSenseiModelTestCase(TestCase):
    """Test cases for MergeSensei models"""
    
    def setUp(self):
        """Set up test data for model tests"""
        self.repository = Repository.objects.create(
            name='test-repo',
            owner='test-owner',
            github_url='https://github.com/test-owner/test-repo'
        )
        
        self.pull_request = PullRequest.objects.create(
            repository=self.repository,
            number=1,
            title='Test PR',
            author='test-author',
            base_branch='main',
            head_branch='feature/test',
            status='open',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            github_url='https://github.com/test-owner/test-repo/pull/1'
        )

    def test_repository_str(self):
        """Test Repository string representation"""
        self.assertEqual(str(self.repository), 'test-owner/test-repo')

    def test_pull_request_str(self):
        """Test PullRequest string representation"""
        self.assertEqual(str(self.pull_request), 'PR #1: Test PR')

    def test_file_change_str(self):
        """Test FileChange string representation"""
        file_change = FileChange.objects.create(
            pull_request=self.pull_request,
            file_path='test.py',
            change_type='modified'
        )
        self.assertEqual(str(file_change), 'test.py (modified)')

    def test_conflict_prediction_str(self):
        """Test ConflictPrediction string representation"""
        pr2 = PullRequest.objects.create(
            repository=self.repository,
            number=2,
            title='Test PR 2',
            author='test-author-2',
            base_branch='main',
            head_branch='feature/test2',
            status='open',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            github_url='https://github.com/test-owner/test-repo/pull/2'
        )
        
        conflict = ConflictPrediction.objects.create(
            pull_request=self.pull_request,
            conflicting_pr=pr2,
            file_path='test.py',
            risk_level='high',
            confidence_score=0.8
        )
        self.assertEqual(str(conflict), 'Conflict: PR #1 vs PR #2')

    def test_recommendation_str(self):
        """Test Recommendation string representation"""
        recommendation = Recommendation.objects.create(
            pull_request=self.pull_request,
            recommendation_type='test',
            title='Test Recommendation',
            description='Test description'
        )
        self.assertEqual(str(recommendation), 'Recommendation for PR #1: Test Recommendation')

    def test_ml_model_str(self):
        """Test MLModel string representation"""
        ml_model = MLModel.objects.create(
            name='test-model',
            version='1.0',
            accuracy_score=0.85
        )
        self.assertEqual(str(ml_model), 'test-model v1.0')

    def test_pull_request_unique_together(self):
        """Test PullRequest unique constraint"""
        # Try to create another PR with same repository and number
        with self.assertRaises(Exception):
            PullRequest.objects.create(
                repository=self.repository,
                number=1,  # Same number
                title='Duplicate PR',
                author='test-author',
                base_branch='main',
                head_branch='feature/duplicate',
                status='open',
                created_at=timezone.now(),
                updated_at=timezone.now(),
                github_url='https://github.com/test-owner/test-repo/pull/1'
            )


class MergeSenseiIntegrationTestCase(APITestCase):
    """Integration tests for MergeSensei workflow"""
    
    def setUp(self):
        """Set up test data for integration tests"""
        self.repository = Repository.objects.create(
            name='integration-test',
            owner='test-owner',
            github_url='https://github.com/test-owner/integration-test'
        )

    def test_full_workflow(self):
        """Test complete workflow from risk analysis to recommendations"""
        # Step 1: Analyze risk
        risk_url = reverse('analyze_risk')
        risk_data = {
            'pr_number': 100,
            'repo_name': 'integration-test',
            'repo_owner': 'test-owner'
        }
        risk_response = self.client.post(risk_url, risk_data, format='json')
        self.assertEqual(risk_response.status_code, status.HTTP_200_OK)
        
        # Step 2: Get recommendations based on conflicts
        rec_url = reverse('get_recommendation')
        rec_data = {
            'pr_number': 100,
            'conflicts': risk_response.data['conflicts']
        }
        rec_response = self.client.post(rec_url, rec_data, format='json')
        self.assertEqual(rec_response.status_code, status.HTTP_200_OK)
        
        # Step 3: Predict conflicts using ML
        predict_url = reverse('predict_conflicts')
        predict_data = {
            'features': {
                'num_files_changed': 2,
                'overlapping_files': 1
            }
        }
        predict_response = self.client.post(predict_url, predict_data, format='json')
        self.assertEqual(predict_response.status_code, status.HTTP_200_OK)
        
        # Verify all responses are valid
        self.assertIn('risk_score', risk_response.data)
        self.assertIn('recommendations', rec_response.data)
        self.assertIn('prediction', predict_response.data)

    def test_multiple_pr_conflict_detection(self):
        """Test conflict detection between multiple PRs"""
        # Create multiple PRs that might conflict
        pr1 = PullRequest.objects.create(
            repository=self.repository,
            number=101,
            title='PR 1',
            author='alice',
            base_branch='main',
            head_branch='feature/1',
            status='open',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            github_url='https://github.com/test-owner/integration-test/pull/101',
            conflict_files=['src/app.py']
        )
        
        pr2 = PullRequest.objects.create(
            repository=self.repository,
            number=102,
            title='PR 2',
            author='bob',
            base_branch='main',
            head_branch='feature/2',
            status='open',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            github_url='https://github.com/test-owner/integration-test/pull/102',
            conflict_files=['src/app.py']
        )
        
        # Analyze risk for PR 101
        risk_url = reverse('analyze_risk')
        risk_data = {
            'pr_number': 101,
            'repo_name': 'integration-test',
            'repo_owner': 'test-owner'
        }
        response = self.client.post(risk_url, risk_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should detect potential conflict with PR 102
        self.assertTrue(len(response.data['conflicts']) > 0)
