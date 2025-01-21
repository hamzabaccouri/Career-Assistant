import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.quality_agents.ats_validator import ATSValidator

class TestATSValidator(unittest.TestCase):
    def setUp(self):
        self.validator = ATSValidator()
        
        self.sample_cv = """
        Senior Software Engineer
        
        Experience:
        - Developed Python applications using Django
        - Led team of 5 developers
        
        Skills:
        - Python, Django, React
        - AWS, Docker
        """
        
        self.sample_job = """
        Senior Software Engineer position:
        - 5+ years Python experience
        - Django and React expertise
        - AWS knowledge required
        """

    @patch('models.model_manager.ModelManager.get_structured_completion')
    @patch('utils.ats_rules.ATSRules.validate_structure')
    def test_validate_cv(self, mock_validate_structure, mock_get_structured):
        # Setup mock responses
        mock_validate_structure.return_value = {
            'valid': True,
            'issues': []
        }
        
        mock_get_structured.side_effect = [
            # Format validation response
            {
                'is_clean_format': True,
                'has_proper_spacing': True,
                'uses_standard_sections': True,
                'formatting_issues': [],
                'format_score': 90
            },
            # Keyword validation response
            {
                'keyword_matches': ['Python', 'Django'],
                'missing_keywords': ['AWS'],
                'keyword_placement_score': 85,
                'optimization_level': 'good'
            },
            # Content validation response
            {
                'content_clarity': 90,
                'bullet_point_quality': 85,
                'achievement_focus': 80,
                'content_issues': []
            }
        ]
        
        # Test validation
        result = self.validator.validate_cv(self.sample_cv, self.sample_job)
        
        # Verify result structure
        self.assertIn('overall_score', result)
        self.assertIn('is_ats_compliant', result)
        self.assertIn('validation_details', result)
        self.assertIn('critical_issues', result)
        self.assertIn('improvement_suggestions', result)
        
        # Verify score range
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)

    def test_calculate_overall_score(self):
        validation_results = {
            'format': {'score': 90, 'passes_validation': True},
            'keywords': {'score': 85, 'passes_validation': True},
            'structure': {'score': 80, 'passes_validation': True},
            'content': {'score': 75, 'passes_validation': True}
        }
        
        score = self.validator._calculate_overall_score(validation_results)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_identify_critical_issues(self):
        validation_results = {
            'format': {
                'passes_validation': False,
                'issues': ['Invalid format']
            },
            'keywords': {
                'passes_validation': False,
                'missing_keywords': ['Python']
            },
            'structure': {
                'passes_validation': True,
                'issues': []
            },
            'content': {
                'passes_validation': True,
                'issues': []
            }
        }
        
        issues = self.validator._identify_critical_issues(validation_results)
        
        self.assertIsInstance(issues, list)
        self.assertGreater(len(issues), 0)

    def test_generate_suggestions(self):
        validation_results = {
            'format': {'passes_validation': False},
            'keywords': {'passes_validation': True},
            'structure': {'passes_validation': False},
            'content': {'passes_validation': True}
        }
        
        suggestions = self.validator._generate_suggestions(validation_results)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)

if __name__ == '__main__':
    unittest.main()