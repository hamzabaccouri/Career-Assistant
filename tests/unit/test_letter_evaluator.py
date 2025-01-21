import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.quality_agents.letter_evaluator import LetterEvaluator

class TestLetterEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = LetterEvaluator()
        
        self.sample_letter = """
        Dear Hiring Manager,

        I am writing to express my interest in the Senior Software Engineer position at Tech Corp.
        With 5 years of experience in Python development and team leadership, I am confident in my
        ability to contribute to your innovative projects.

        Best regards,
        John Doe
        """
        
        self.sample_job = """
        Senior Software Engineer position:
        - 5+ years Python experience
        - Team leadership skills
        - Experience with cloud technologies
        """

    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_evaluate_letter(self, mock_get_structured):
        # Setup mock responses
        mock_get_structured.side_effect = [
            # Content relevance response
            {
                'relevance_score': 85,
                'key_requirements_addressed': ['Python experience', 'Team leadership'],
                'missing_requirements': ['Cloud experience'],
                'effectiveness': 80
            },
            # Professional tone response
            {
                'tone_score': 90,
                'language_quality': 85,
                'professionalism_issues': [],
                'strong_elements': ['Clear communication']
            },
            # Customization response
            {
                'customization_score': 85,
                'company_specific_content': ['Company name', 'Position'],
                'generic_elements': ['Standard closing'],
                'personalization_level': 80
            },
            # Structure format response
            {
                'structure_score': 88,
                'formatting_score': 85,
                'structure_issues': [],
                'format_strengths': ['Proper formatting']
            }
        ]
        
        # Test evaluation
        result = self.evaluator.evaluate_letter(
            self.sample_letter,
            self.sample_job,
            "Tech Corp"
        )
        
        # Verify result structure
        self.assertIn('overall_score', result)
        self.assertIn('evaluation_summary', result)
        self.assertIn('meets_standards', result)
        self.assertIn('strong_points', result)
        self.assertIn('improvement_needed', result)
        
        # Verify score ranges
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)

    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_evaluate_content_relevance(self, mock_get_structured):
        mock_get_structured.return_value = {
            'relevance_score': 85,
            'key_requirements_addressed': ['Python experience'],
            'missing_requirements': ['Cloud experience'],
            'effectiveness': 80
        }
        
        result = self.evaluator._evaluate_content_relevance(
            self.sample_letter,
            self.sample_job
        )
        
        self.assertIn('score', result)
        self.assertIn('addressed_requirements', result)
        self.assertIn('missing_requirements', result)

    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_evaluate_professional_tone(self, mock_get_structured):
        mock_get_structured.return_value = {
            'tone_score': 90,
            'language_quality': 85,
            'professionalism_issues': [],
            'strong_elements': ['Clear communication']
        }
        
        result = self.evaluator._evaluate_professional_tone(self.sample_letter)
        
        self.assertIn('score', result)
        self.assertIn('issues', result)
        self.assertIn('strengths', result)

    def test_check_minimum_standards(self):
        scores = {
            'content_relevance': 85,
            'professional_tone': 90,
            'customization': 75,
            'structure_format': 80
        }
        
        result = self.evaluator._check_minimum_standards(scores)
        
        self.assertIn('meets_all_standards', result)
        self.assertIn('criteria_results', result)
        self.assertIsInstance(result['meets_all_standards'], bool)

    def test_identify_strengths(self):
        evaluation_results = {
            'content': {
                'score': 85,
                'addressed_requirements': ['Python', 'Leadership']
            },
            'tone': {
                'score': 90,
                'strengths': ['Professional tone']
            },
            'custom': {
                'score': 85,
                'company_specific': ['Company reference']
            },
            'format': {
                'score': 88,
                'strengths': ['Good structure']
            }
        }
        
        strengths = self.evaluator._identify_strengths(evaluation_results)
        
        self.assertIsInstance(strengths, list)
        self.assertGreater(len(strengths), 0)

    def test_identify_improvements(self):
        evaluation_results = {
            'content': {
                'score': 65,
                'missing_requirements': ['Cloud experience']
            },
            'tone': {
                'score': 60,
                'issues': ['Too informal']
            },
            'custom': {
                'score': 65,
                'generic_elements': ['Generic closing']
            },
            'format': {
                'score': 60,
                'issues': ['Improve spacing']
            }
        }
        
        improvements = self.evaluator._identify_improvements(evaluation_results)
        
        self.assertIsInstance(improvements, list)
        self.assertGreater(len(improvements), 0)

if __name__ == '__main__':
    unittest.main()