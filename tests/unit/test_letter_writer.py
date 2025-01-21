import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.primary_agents.letter_writer import LetterWriter

class TestLetterWriter(unittest.TestCase):
    def setUp(self):
        self.writer = LetterWriter()
        
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

    @patch('agents.primary_agents.job_analyzer.JobAnalyzer.analyze_job')
    @patch('agents.primary_agents.cv_matcher.CVMatcher.match_cv_to_job')
    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_generate_cover_letter(self, mock_get_structured, mock_match, mock_analyze_job):
        # Setup mock responses
        mock_analyze_job.return_value = {
            'requirements': {
                'required_skills': ['Python', 'Django'],
                'experience': '5+ years'
            },
            'company_culture': {
                'indicators': ['Innovative', 'Collaborative']
            }
        }
        
        mock_match.return_value = {
            'skills_match': {
                'matched_required': ['Python', 'Django']
            },
            'experience_match': {
                'meets_requirement': True
            }
        }
        
        mock_get_structured.return_value = {
            'introduction': 'Test introduction',
            'body_paragraphs': ['Test paragraph 1', 'Test paragraph 2'],
            'closing': 'Test closing',
            'achievements': ['Achievement 1'],
            'key_points': ['Key point 1']
        }
        
        # Test letter generation
        result = self.writer.generate_cover_letter(
            self.sample_cv,
            self.sample_job,
            "Test Company"
        )
        
        # Verify result structure
        self.assertIn('letter', result)
        self.assertIn('structure', result)
        self.assertIn('style_analysis', result)
        self.assertIn('matching_achievements', result)

    def test_format_letter(self):
        content = {
            'introduction': 'Test introduction',
            'body_paragraphs': ['Test paragraph 1', 'Test paragraph 2'],
            'closing': 'Test closing'
        }
        
        # Test formal format
        formal_result = self.writer._format_letter(
            content,
            "Test Company",
            'formal'
        )
        
        self.assertIn('final_letter', formal_result)
        self.assertIn('sections', formal_result)
        self.assertIn('company_address', formal_result['sections'])
        
        # Test modern format
        modern_result = self.writer._format_letter(
            content,
            "Test Company",
            'modern'
        )
        
        self.assertNotIn('company_address', modern_result['sections'])

    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_validate_letter(self, mock_get_structured):
        mock_get_structured.return_value = {
            'is_relevant': True,
            'addresses_key_requirements': True,
            'professional_tone': True,
            'improvement_suggestions': ['Add more specifics']
        }
        
        result = self.writer.validate_letter(
            "Test letter content",
            self.sample_job
        )
        
        self.assertIn('is_relevant', result)
        self.assertIn('addresses_key_requirements', result)
        self.assertIn('professional_tone', result)
        self.assertIn('improvement_suggestions', result)

if __name__ == '__main__':
    unittest.main()