"""
AI Integration module for MergeSensei
Handles OpenRouter, Cohere, and ML model integration
"""

import os
import json
import requests
import cohere
import openai
from typing import Dict, List, Any, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Base AI service class"""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        # Initialize Cohere client
        if self.cohere_api_key:
            self.cohere_client = cohere.Client(api_key=self.cohere_api_key)
        else:
            self.cohere_client = None
            
        # Initialize OpenAI client for OpenRouter
        if self.openrouter_api_key:
            openai.api_key = self.openrouter_api_key
            openai.api_base = "https://openrouter.ai/api/v1"
        else:
            openai.api_key = None

    def is_available(self) -> bool:
        """Check if AI service is available"""
        return bool(self.openrouter_api_key or self.cohere_api_key)


class ConflictPredictionAI(AIService):
    """AI service for conflict prediction and analysis"""
    
    def analyze_conflict_risk(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze conflict risk using AI
        """
        try:
            if not self.is_available():
                return self._fallback_analysis(pr_data)
            
            # Prepare context for AI analysis
            context = self._prepare_context(pr_data)
            
            # Use Cohere for analysis (more reliable for this use case)
            if self.cohere_client:
                return self._cohere_analysis(context, pr_data)
            else:
                return self._openrouter_analysis(context, pr_data)
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(pr_data)
    
    def _prepare_context(self, pr_data: Dict[str, Any]) -> str:
        """Prepare context for AI analysis"""
        context = f"""
        Pull Request Analysis:
        - PR Number: {pr_data.get('number', 'N/A')}
        - Title: {pr_data.get('title', 'N/A')}
        - Author: {pr_data.get('author', 'N/A')}
        - Base Branch: {pr_data.get('base_branch', 'N/A')}
        - Head Branch: {pr_data.get('head_branch', 'N/A')}
        - Files Changed: {pr_data.get('conflict_files', [])}
        - Lines Added: {pr_data.get('lines_added', 0)}
        - Lines Removed: {pr_data.get('lines_removed', 0)}
        - Other Open PRs: {pr_data.get('other_open_prs', [])}
        """
        return context
    
    def _cohere_analysis(self, context: str, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Cohere for conflict analysis"""
        try:
            prompt = f"""
            As a Git conflict prediction expert, analyze this pull request for potential merge conflicts.
            
            {context}
            
            Please provide:
            1. Risk score (0.0 to 1.0)
            2. Risk level (low/medium/high)
            3. Confidence score (0.0 to 1.0)
            4. Specific files at risk
            5. Potential conflict scenarios
            6. Recommended actions
            
            Respond in JSON format:
            {{
                "risk_score": 0.0-1.0,
                "risk_level": "low/medium/high",
                "confidence": 0.0-1.0,
                "at_risk_files": ["file1", "file2"],
                "conflict_scenarios": ["scenario1", "scenario2"],
                "recommendations": ["action1", "action2"]
            }}
            """
            
            response = self.cohere_client.chat(
                model='command-r-plus-08-2024',
                message=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse the response
            result_text = response.text.strip()
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = result_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError):
                # Fallback parsing
                result = self._parse_text_response(result_text)
            
            return {
                'risk_score': float(result.get('risk_score', 0.5)),
                'risk_level': result.get('risk_level', 'medium'),
                'confidence': float(result.get('confidence', 0.7)),
                'at_risk_files': result.get('at_risk_files', []),
                'conflict_scenarios': result.get('conflict_scenarios', []),
                'recommendations': result.get('recommendations', []),
                'ai_model': 'cohere-command-r-plus',
                'analysis_type': 'ai_powered'
            }
            
        except Exception as e:
            logger.error(f"Cohere analysis failed: {e}")
            return self._fallback_analysis(pr_data)
    
    def _openrouter_analysis(self, context: str, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenRouter for conflict analysis"""
        try:
            prompt = f"""
            As a Git conflict prediction expert, analyze this pull request for potential merge conflicts.
            
            {context}
            
            Please provide:
            1. Risk score (0.0 to 1.0)
            2. Risk level (low/medium/high)
            3. Confidence score (0.0 to 1.0)
            4. Specific files at risk
            5. Potential conflict scenarios
            6. Recommended actions
            
            Respond in JSON format:
            {{
                "risk_score": 0.0-1.0,
                "risk_level": "low/medium/high",
                "confidence": 0.0-1.0,
                "at_risk_files": ["file1", "file2"],
                "conflict_scenarios": ["scenario1", "scenario2"],
                "recommendations": ["action1", "action2"]
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="meta-llama/llama-3-8b-instruct:free",
                messages=[
                    {"role": "system", "content": "You are a Git conflict prediction expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                result = self._parse_text_response(result_text)
            
            return {
                'risk_score': float(result.get('risk_score', 0.5)),
                'risk_level': result.get('risk_level', 'medium'),
                'confidence': float(result.get('confidence', 0.7)),
                'at_risk_files': result.get('at_risk_files', []),
                'conflict_scenarios': result.get('conflict_scenarios', []),
                'recommendations': result.get('recommendations', []),
                'ai_model': 'llama-3-8b',
                'analysis_type': 'ai_powered'
            }
            
        except Exception as e:
            logger.error(f"OpenRouter analysis failed: {e}")
            return self._fallback_analysis(pr_data)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        # Simple text parsing fallback
        risk_score = 0.5
        risk_level = "medium"
        confidence = 0.7
        
        text_lower = text.lower()
        
        if "high risk" in text_lower or "high-risk" in text_lower:
            risk_score = 0.8
            risk_level = "high"
        elif "low risk" in text_lower or "low-risk" in text_lower:
            risk_score = 0.2
            risk_level = "low"
        
        if "confidence" in text_lower:
            # Try to extract confidence score
            import re
            conf_match = re.search(r'confidence[:\s]+([0-9.]+)', text_lower)
            if conf_match:
                confidence = float(conf_match.group(1))
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'confidence': confidence,
            'at_risk_files': [],
            'conflict_scenarios': [],
            'recommendations': []
        }
    
    def _fallback_analysis(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        conflict_files = pr_data.get('conflict_files', [])
        other_prs = pr_data.get('other_open_prs', [])
        
        # Simple rule-based analysis
        risk_score = 0.3
        if len(conflict_files) > 0:
            risk_score += 0.3
        if len(other_prs) > 0:
            risk_score += 0.2
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score > 0.7:
            risk_level = "high"
        elif risk_score > 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'confidence': 0.6,
            'at_risk_files': conflict_files,
            'conflict_scenarios': [],
            'recommendations': [
                "Review conflicting files carefully",
                "Coordinate with other developers",
                "Consider rebasing before merging"
            ],
            'ai_model': 'rule_based',
            'analysis_type': 'fallback'
        }


class RecommendationAI(AIService):
    """AI service for generating intelligent recommendations"""
    
    def generate_recommendations(self, pr_data: Dict[str, Any], conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate AI-powered recommendations for conflict resolution
        """
        try:
            if not self.is_available():
                return self._fallback_recommendations(pr_data, conflicts)
            
            context = self._prepare_recommendation_context(pr_data, conflicts)
            
            if self.cohere_client:
                return self._cohere_recommendations(context, pr_data, conflicts)
            else:
                return self._openrouter_recommendations(context, pr_data, conflicts)
                
        except Exception as e:
            logger.error(f"AI recommendation generation failed: {e}")
            return self._fallback_recommendations(pr_data, conflicts)
    
    def _prepare_recommendation_context(self, pr_data: Dict[str, Any], conflicts: List[Dict[str, Any]]) -> str:
        """Prepare context for recommendation generation"""
        context = f"""
        Pull Request Context:
        - PR #{pr_data.get('number', 'N/A')}: {pr_data.get('title', 'N/A')}
        - Author: {pr_data.get('author', 'N/A')}
        - Files Changed: {pr_data.get('conflict_files', [])}
        - Risk Level: {pr_data.get('risk_level', 'medium')}
        
        Conflicts Detected:
        """
        
        for i, conflict in enumerate(conflicts, 1):
            context += f"""
        Conflict {i}:
        - Conflicting PR: #{conflict.get('conflicting_pr_number', 'N/A')}
        - Files: {conflict.get('conflicting_files', [])}
        - Risk Level: {conflict.get('risk_level', 'medium')}
        """
        
        return context
    
    def _cohere_recommendations(self, context: str, pr_data: Dict[str, Any], conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommendations using Cohere"""
        try:
            prompt = f"""
            As a Git workflow expert, provide specific, actionable recommendations for resolving merge conflicts.
            
            {context}
            
            Generate 3-5 specific recommendations with:
            1. Type (sync_suggestion, review_suggestion, communication_suggestion, merge_strategy, etc.)
            2. Title (short, clear)
            3. Description (detailed, actionable)
            4. Priority (low/medium/high)
            5. Action (what the developer should do)
            
            Respond in JSON format:
            {{
                "recommendations": [
                    {{
                        "type": "sync_suggestion",
                        "title": "Sync with conflicting PR",
                        "description": "Detailed description...",
                        "priority": "high",
                        "action": "sync_branches"
                    }}
                ]
            }}
            """
            
            response = self.cohere_client.chat(
                model='command-r-plus-08-2024',
                message=prompt,
                max_tokens=800,
                temperature=0.4
            )
            
            result_text = response.text.strip()
            
            try:
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = result_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    return result.get('recommendations', [])
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError):
                return self._fallback_recommendations(pr_data, conflicts)
                
        except Exception as e:
            logger.error(f"Cohere recommendations failed: {e}")
            return self._fallback_recommendations(pr_data, conflicts)
    
    def _openrouter_recommendations(self, context: str, pr_data: Dict[str, Any], conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommendations using OpenRouter"""
        try:
            prompt = f"""
            As a Git workflow expert, provide specific, actionable recommendations for resolving merge conflicts.
            
            {context}
            
            Generate 3-5 specific recommendations with:
            1. Type (sync_suggestion, review_suggestion, communication_suggestion, merge_strategy, etc.)
            2. Title (short, clear)
            3. Description (detailed, actionable)
            4. Priority (low/medium/high)
            5. Action (what the developer should do)
            
            Respond in JSON format:
            {{
                "recommendations": [
                    {{
                        "type": "sync_suggestion",
                        "title": "Sync with conflicting PR",
                        "description": "Detailed description...",
                        "priority": "high",
                        "action": "sync_branches"
                    }}
                ]
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="meta-llama/llama-3-8b-instruct:free",
                messages=[
                    {"role": "system", "content": "You are a Git workflow expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(result_text)
                return result.get('recommendations', [])
            except json.JSONDecodeError:
                return self._fallback_recommendations(pr_data, conflicts)
                
        except Exception as e:
            logger.error(f"OpenRouter recommendations failed: {e}")
            return self._fallback_recommendations(pr_data, conflicts)
    
    def _fallback_recommendations(self, pr_data: Dict[str, Any], conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback recommendations when AI is not available"""
        recommendations = []
        
        if conflicts:
            recommendations.append({
                'type': 'sync_suggestion',
                'title': 'Sync with conflicting PRs',
                'description': 'Multiple PRs are modifying the same files. Consider syncing branches before merging to avoid conflicts.',
                'priority': 'high',
                'action': 'sync_branches'
            })
        
        recommendations.extend([
            {
                'type': 'review_suggestion',
                'title': 'Review conflicting files',
                'description': 'Carefully review all files that might have conflicts before merging.',
                'priority': 'medium',
                'action': 'manual_review'
            },
            {
                'type': 'communication_suggestion',
                'title': 'Coordinate with team',
                'description': 'Communicate with other developers working on conflicting changes to coordinate merge timing.',
                'priority': 'high',
                'action': 'team_communication'
            },
            {
                'type': 'merge_strategy',
                'title': 'Plan merge strategy',
                'description': 'Consider using rebase or merge strategies to minimize conflicts.',
                'priority': 'medium',
                'action': 'plan_merge_strategy'
            }
        ])
        
        return recommendations


class MLModelService:
    """Service for ML model training and prediction"""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    def train_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train ML model on historical conflict data
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, classification_report
            import pandas as pd
            import numpy as np
            
            # Prepare features and labels
            df = pd.DataFrame(training_data)
            
            # Feature engineering
            features = self._extract_features(df)
            labels = df['conflict_occurred'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.is_trained = True
            
            return {
                'accuracy': accuracy,
                'model_type': 'RandomForestClassifier',
                'features_used': list(features.columns),
                'training_samples': len(training_data),
                'status': 'trained'
            }
            
        except Exception as e:
            logger.error(f"ML model training failed: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    def predict_conflict(self, pr_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict conflict probability using trained model
        """
        if not self.is_trained or self.model is None:
            return {'error': 'Model not trained', 'confidence': 0.0}
        
        try:
            import pandas as pd
            
            # Convert features to DataFrame
            features_df = pd.DataFrame([pr_features])
            features = self._extract_features(features_df)
            
            # Predict
            probability = self.model.predict_proba(features)[0]
            prediction = self.model.predict(features)[0]
            
            return {
                'conflict_probability': float(probability[1]),  # Probability of conflict
                'prediction': bool(prediction),
                'confidence': float(max(probability)),
                'model_type': 'RandomForestClassifier'
            }
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {'error': str(e), 'confidence': 0.0}
    
    def _extract_features(self, df) -> 'pd.DataFrame':
        """Extract features for ML model"""
        import pandas as pd
        
        features = pd.DataFrame()
        
        # Basic features
        features['num_files_changed'] = df.get('num_files_changed', 0)
        features['lines_added'] = df.get('lines_added', 0)
        features['lines_removed'] = df.get('lines_removed', 0)
        features['num_developers'] = df.get('num_developers', 1)
        features['days_since_creation'] = df.get('days_since_creation', 0)
        
        # Conflict-related features
        features['has_conflicting_files'] = df.get('has_conflicting_files', False).astype(int)
        features['num_conflicting_prs'] = df.get('num_conflicting_prs', 0)
        features['overlapping_files'] = df.get('overlapping_files', 0)
        
        # Fill NaN values
        features = features.fillna(0)
        
        return features
