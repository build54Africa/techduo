"""
GitHub integration service for MergeSensei
Handles fetching real repository and PR data from GitHub
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.api_base = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'MergeSensei/1.0'
        }
        
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
    
    def is_available(self) -> bool:
        """Check if GitHub service is available"""
        return bool(self.github_token)
    
    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            return {
                'name': data['name'],
                'full_name': data['full_name'],
                'owner': data['owner']['login'],
                'description': data['description'],
                'html_url': data['html_url'],
                'clone_url': data['clone_url'],
                'default_branch': data['default_branch'],
                'language': data['language'],
                'stars': data['stargazers_count'],
                'forks': data['forks_count'],
                'open_issues': data['open_issues_count'],
                'created_at': data['created_at'],
                'updated_at': data['updated_at']
            }
        except Exception as e:
            logger.error(f"Failed to fetch repository info: {e}")
            raise
    
    def get_pull_requests(self, owner: str, repo: str, state: str = 'open', per_page: int = 30) -> List[Dict[str, Any]]:
        """Get pull requests from repository"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/pulls"
            params = {
                'state': state,
                'per_page': per_page,
                'sort': 'updated',
                'direction': 'desc'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            prs = response.json()
            processed_prs = []
            
            for pr in prs:
                processed_pr = self._process_pull_request(pr, owner, repo)
                processed_prs.append(processed_pr)
            
            return processed_prs
            
        except Exception as e:
            logger.error(f"Failed to fetch pull requests: {e}")
            raise
    
    def get_pull_request_details(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get detailed information about a specific pull request"""
        try:
            # Get PR details
            pr_url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}"
            pr_response = requests.get(pr_url, headers=self.headers)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            # Get PR files
            files_url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            files_response = requests.get(files_url, headers=self.headers)
            files_response.raise_for_status()
            files_data = files_response.json()
            
            # Process the data
            processed_pr = self._process_pull_request(pr_data, owner, repo)
            processed_pr['files'] = self._process_pr_files(files_data)
            
            return processed_pr
            
        except Exception as e:
            logger.error(f"Failed to fetch PR details: {e}")
            raise
    
    def _process_pull_request(self, pr_data: Dict[str, Any], owner: str, repo: str) -> Dict[str, Any]:
        """Process raw PR data into our format"""
        return {
            'number': pr_data['number'],
            'title': pr_data['title'],
            'body': pr_data['body'],
            'author': pr_data['user']['login'],
            'author_avatar': pr_data['user']['avatar_url'],
            'base_branch': pr_data['base']['ref'],
            'head_branch': pr_data['head']['ref'],
            'status': pr_data['state'],
            'created_at': pr_data['created_at'],
            'updated_at': pr_data['updated_at'],
            'merged_at': pr_data['merged_at'],
            'closed_at': pr_data['closed_at'],
            'html_url': pr_data['html_url'],
            'diff_url': pr_data['diff_url'],
            'patch_url': pr_data['patch_url'],
            'commits': pr_data['commits'],
            'additions': pr_data['additions'],
            'deletions': pr_data['deletions'],
            'changed_files': pr_data['changed_files'],
            'mergeable': pr_data['mergeable'],
            'mergeable_state': pr_data['mergeable_state'],
            'draft': pr_data['draft'],
            'labels': [label['name'] for label in pr_data['labels']],
            'assignees': [assignee['login'] for assignee in pr_data['assignees']],
            'reviewers': [reviewer['login'] for reviewer in pr_data['requested_reviewers']],
            'repository': {
                'owner': owner,
                'name': repo,
                'full_name': f"{owner}/{repo}"
            }
        }
    
    def _process_pr_files(self, files_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process PR files data"""
        processed_files = []
        
        for file_data in files_data:
            processed_file = {
                'filename': file_data['filename'],
                'status': file_data['status'],  # added, modified, removed, renamed
                'additions': file_data['additions'],
                'deletions': file_data['deletions'],
                'changes': file_data['changes'],
                'blob_url': file_data['blob_url'],
                'raw_url': file_data['raw_url'],
                'contents_url': file_data['contents_url'],
                'patch': file_data.get('patch', ''),
                'previous_filename': file_data.get('previous_filename')
            }
            processed_files.append(processed_file)
        
        return processed_files
    
    def get_repository_commits(self, owner: str, repo: str, since: str = None, per_page: int = 30) -> List[Dict[str, Any]]:
        """Get recent commits from repository"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/commits"
            params = {
                'per_page': per_page,
                'sort': 'committer-date',
                'direction': 'desc'
            }
            
            if since:
                params['since'] = since
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            commits = response.json()
            processed_commits = []
            
            for commit in commits:
                processed_commit = {
                    'sha': commit['sha'],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'author_email': commit['commit']['author']['email'],
                    'committer': commit['commit']['committer']['name'],
                    'committer_email': commit['commit']['committer']['email'],
                    'date': commit['commit']['committer']['date'],
                    'html_url': commit['html_url'],
                    'parents': [parent['sha'] for parent in commit['parents']]
                }
                processed_commits.append(processed_commit)
            
            return processed_commits
            
        except Exception as e:
            logger.error(f"Failed to fetch commits: {e}")
            raise
    
    def search_repositories(self, query: str, language: str = None, sort: str = 'stars') -> List[Dict[str, Any]]:
        """Search for repositories"""
        try:
            url = f"{self.api_base}/search/repositories"
            params = {
                'q': query,
                'sort': sort,
                'per_page': 20
            }
            
            if language:
                params['q'] += f' language:{language}'
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            repositories = []
            
            for repo in data['items']:
                repository = {
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'owner': repo['owner']['login'],
                    'description': repo['description'],
                    'html_url': repo['html_url'],
                    'language': repo['language'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'open_issues': repo['open_issues_count'],
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at']
                }
                repositories.append(repository)
            
            return repositories
            
        except Exception as e:
            logger.error(f"Failed to search repositories: {e}")
            raise
