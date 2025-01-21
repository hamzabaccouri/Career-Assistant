import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.quality_agents.cv_evaluator import CVEvaluator

class TestCVEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = CVEvaluator()
        
        self.sample_cv = """
        Senior Software Engineer
        
        Experience:
        - Developed Python applications using Django
        - Led team of 5 developers
        - Increased system performance by 40%
        
        Skills:
        - Python, Django, React
        - AWS, Docker
        - Team Leadership
        """

    @patch('agents.primary_agents.cv_analyzer.CVAnalyzer.analyze_cv')
    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_evaluate_cv(self, mock_get_structured, mock_analyze_cv):
        # Setup mock responses
        mock_analyze_cv.return_value = {
            'skills': ['Python', 'Django'],
            'experience_years': 5,
            'achievements': ['Led team', 'Increased performance']
        }
        
        mock_get_structured.side_effect = [
            # Content quality response
            {
                'clarity_score': 90,
                'conciseness_score': 85,
                'professionalism_score': 88,
                'content_issues': [],
                'strong_points': ['Clear structure']
            },
            # Achievements response
            {
                'quantification_score': 85,
                'impact_score': 90,
                'relevance_score': 88,
                'weak_achievements': [],
                'strong_achievements': ['Performance improvement']
            },
            # Experience response
            {
                'progression_clarity': 85,
                'role_description_quality': 88,
                'responsibility_clarity': 90,
                'improvement_areas': [],
                'effective_points': ['Clear role progression']
            },
            # Skills response
            {
                'organization_score': 90,
                'relevance_score': 85,
                'specificity_score': 88,
                'missing_key_skills': [],
                'well_presented_skills': ['Python', 'Django']
            }
        ]
        
        # Test evaluation
        result = self.evaluator.evaluate_cv(self.sample_cv, "Technology")
        
        # Verify result structure
        self.assertIn('overall_score', result)
        self.assertIn('evaluation_summary', result)
        self.assertIn('strengths', result)
        self.assertIn('improvement_areas', result)
        
        # Verify score ranges
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)

    def test_calculate_overall_score(self):
        evaluation_results = {
            'content': {'score': 90},
            'achievements': {'score': 85},
            'experience': {'score': 88},
            'skills': {'score': 92}
        }
        
        score = self.evaluator._calculate_overall_score(evaluation_results)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_identify_strengths(self):
        evaluation_results = {
            'content': {
                'score': 90,
                'strengths': ['Clear writing']
            },
            'achievements': {
                'score': 85,
                'strong_points': ['Quantified results']
            },
            'experience': {
                'score': 88,
                'effective_aspects': ['Good progression']
            },
            'skills': {
                'score': 92,
                'strong_skills': ['Technical skills']
            }
        }
        
        strengths = self.evaluator._identify_strengths(evaluation_results)
        
        self.assertIsInstance(strengths, list)
        self.assertGreater(len(strengths), 0)

    def test_identify_improvements(self):
        evaluation_results = {
            'content': {
                'score': 70,
                'issues': ['Need more detail']
            },
            'achievements': {
                'score': 75,
                'weak_points': ['Lack of metrics']
            },
            'experience': {
                'score': 72,
                'improvements': ['Add more context']
            },
            'skills': {
                'score': 70,
                'missing_skills': ['Leadership']
            }
        }
        
        improvements = self.evaluator._identify_improvements(evaluation_results)
        
        self.assertIsInstance(improvements, list)
        self.assertGreater(len(improvements), 0)

    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_evaluate_industry_alignment(self, mock_get_structured):
        mock_get_structured.return_value = {
            'alignment_score': 85,
            'industry_specific_strengths': ['Relevant tech stack'],
            'industry_gaps': ['Cloud certification'],
            'industry_recommendations': ['Add AWS certification']
        }
        
        result = self.evaluator._evaluate_industry_alignment(
            self.sample_cv,
            "Technology"
        )
        
        self.assertIn('alignment_score', result)
        self.assertIn('industry_strengths', result)
        self.assertIn('industry_gaps', result)
        self.assertIn('recommendations', result)

if __name__ == '__main__':
    unittest.main()