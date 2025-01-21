# tests/unit/test_cv_analyzer.py
import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

load_dotenv()

from agents.primary_agents.cv_analyzer import CVAnalyzer

class TestCVAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CVAnalyzer()
        
        self.sample_cv = """
        Senior Software Engineer
        
        Experience:
        - Developed Python applications using Django
        - Led team of 5 developers
        
        Skills:
        - Python, Django, React
        - AWS, Docker
        """

    @patch('models.model_manager.ModelManager.analyze_cv')
    @patch('utils.text_analyzer.TextAnalyzer.extract_keywords')
    def test_analyze_cv(self, mock_extract_keywords, mock_analyze_cv):
        # Setup mock responses
        mock_analyze_cv.return_value = {
            'skills': ['Python', 'Django'],
            'experience_years': 5,
            'key_achievements': ['Led team'],
            'improvement_suggestions': ['Add more details']
        }
        
        mock_extract_keywords.return_value = {
            'technical_terms': ['Python', 'Django', 'React'],
            'nouns': ['Engineer', 'Team Lead']
        }
        
        # Test analysis
        result = self.analyzer.analyze_cv(self.sample_cv)
        
        # Verify result structure
        self.assertIn('skills', result)
        self.assertIn('experience', result)
        self.assertIn('ats_compliance', result)
        self.assertIn('improvements', result)
        
        # Verify mocks were called
        mock_analyze_cv.assert_called_once()
        mock_extract_keywords.assert_called_once()

    def test_validate_ats_compliance(self):
        result = self.analyzer.validate_ats_compliance(self.sample_cv)
        self.assertIn('is_compliant', result)
        self.assertIn('issues', result)
        self.assertIn('format_score', result)

    def test_get_cv_score(self):
        analysis = {
            'skills': {
                'technical_skills': ['Python', 'Django'],
                'soft_skills': ['Leadership'],
                'missing_critical_skills': []
            },
            'experience': {
                'years': 5,
                'key_achievements': ['Led team', 'Improved performance']
            },
            'ats_compliance': {
                'format_score': 80
            },
            'improvements': {
                'suggestions': ['Add more details']
            }
        }
        
        score = self.analyzer.get_cv_score(analysis)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

if __name__ == '__main__':
    unittest.main()