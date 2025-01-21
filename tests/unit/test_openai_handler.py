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

from models.openai_handler import OpenAIHandler

class TestOpenAIHandler(unittest.TestCase):
    def setUp(self):
        self.handler = OpenAIHandler()
        
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

    @patch('openai.resources.chat.completions.Completions.create')
    def test_get_completion(self, mock_create):
        # Setup mock
        mock_create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Test response"
                    )
                )
            ]
        )
        
        response = self.handler.get_completion("Test prompt")
        self.assertEqual(response, "Test response")

    @patch('openai.resources.chat.completions.Completions.create')
    def test_get_structured_completion(self, mock_create):
        # Setup mock with proper JSON response
        mock_json_response = {"test": "value"}
        mock_create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content=json.dumps(mock_json_response)
                    )
                )
            ]
        )
        
        schema = {"test": "string"}
        response = self.handler.get_structured_completion("Test prompt", schema)
        self.assertIsInstance(response, dict)
        self.assertIn('test', response)

    @patch('openai.resources.chat.completions.Completions.create')
    def test_analyze_cv(self, mock_create):
        # Setup mock with proper JSON response
        mock_json = {
            "skills": ["Python", "Django"],
            "experience_years": 5,
            "key_achievements": ["Led team"],
            "missing_elements": ["Certifications"],
            "improvement_suggestions": ["Add more details"]
        }
        mock_create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content=json.dumps(mock_json)
                    )
                )
            ]
        )
        
        response = self.handler.analyze_cv(self.sample_cv)
        self.assertIsInstance(response, dict)
        self.assertIn('skills', response)
        self.assertIn('experience_years', response)

    @patch('openai.resources.chat.completions.Completions.create')
    def test_match_job(self, mock_create):
        # Setup mock with proper JSON response
        mock_json = {
            "match_percentage": 85,
            "matching_skills": ["Python", "Django"],
            "missing_skills": ["GraphQL"],
            "recommendations": ["Highlight AWS experience"]
        }
        mock_create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content=json.dumps(mock_json)
                    )
                )
            ]
        )
        
        response = self.handler.match_job(self.sample_cv, self.sample_job)
        self.assertIsInstance(response, dict)
        self.assertIn('match_percentage', response)
        self.assertIn('matching_skills', response)

if __name__ == '__main__':
    unittest.main()