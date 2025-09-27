#!/usr/bin/env python
"""
Test script for AI integration
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/samuel/techduo/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MergeSensei.settings')
django.setup()

from core.ai_integration import ConflictPredictionAI, RecommendationAI, MLModelService

def test_ai_services():
    """Test AI services"""
    print("Testing AI Services...")
    
    # Test conflict prediction AI
    print("\n1. Testing Conflict Prediction AI...")
    conflict_ai = ConflictPredictionAI()
    print(f"Conflict AI available: {conflict_ai.is_available()}")
    
    if conflict_ai.is_available():
        test_pr_data = {
            'number': 123,
            'title': 'Update dashboard component',
            'author': 'alice',
            'base_branch': 'main',
            'head_branch': 'feature/dashboard',
            'conflict_files': ['src/dashboard.html', 'src/components/Header.js'],
            'lines_added': 50,
            'lines_removed': 10,
            'other_open_prs': [
                {
                    'number': 124,
                    'title': 'Add new dashboard features',
                    'conflict_files': ['src/dashboard.html']
                }
            ]
        }
        
        result = conflict_ai.analyze_conflict_risk(test_pr_data)
        print(f"AI Analysis Result: {result}")
    
    # Test recommendation AI
    print("\n2. Testing Recommendation AI...")
    rec_ai = RecommendationAI()
    print(f"Recommendation AI available: {rec_ai.is_available()}")
    
    if rec_ai.is_available():
        test_conflicts = [
            {
                'conflicting_pr_number': 124,
                'conflicting_files': ['src/dashboard.html'],
                'risk_level': 'high'
            }
        ]
        
        recommendations = rec_ai.generate_recommendations(test_pr_data, test_conflicts)
        print(f"AI Recommendations: {recommendations}")
    
    # Test ML service
    print("\n3. Testing ML Service...")
    ml_service = MLModelService()
    print(f"ML Service initialized: {ml_service is not None}")
    
    print("\nAI Services test completed!")

if __name__ == "__main__":
    test_ai_services()