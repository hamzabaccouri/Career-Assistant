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

from models.anthropic_handler import AnthropicHandler

class TestAnthropicHandler(unittest.TestCase):
    def setUp(self):
        self.handler = AnthropicHandler()
        
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

    @patch('anthropic.Client')
    def test_get_completion(self, mock_client):
        # Create a complete mock structure
        mock_instance = Mock()
        mock_messages = Mock()
        mock_messages.create.return_value = Mock(
            content=[
                Mock(text="Test response")
            ]
        )
        mock_instance.messages = mock_messages
        mock_client.return_value = mock_instance

        # Test
        handler = AnthropicHandler()
        response = handler.get_completion("Test prompt")
        
        # Assertions
        self.assertEqual(response, "Test response")
        mock_messages.create.assert_called_once()

    @patch('anthropic.Client')
    def test_get_structured_completion(self, mock_client):
        mock_response = Mock()
        mock_response.content = [Mock(text='{"test": "value"}')]
        
        mock_instance = Mock()
        mock_instance.messages.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        schema = {"test": "string"}
        response = self.handler.get_structured_completion("Test prompt", schema)
        self.assertIsInstance(response, dict)
        self.assertIn('test', response)

    @patch('anthropic.Client')
    def test_analyze_cv(self, mock_client):
        mock_json = {
            "skills": ["Python", "Django"],
            "experience_years": 5,
            "key_achievements": ["Led team"],
            "missing_elements": ["Certifications"],
            "improvement_suggestions": ["Add more details"]
        }
        
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps(mock_json))]
        
        mock_instance = Mock()
        mock_instance.messages.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        response = self.handler.analyze_cv(self.sample_cv)
        self.assertIsInstance(response, dict)
        self.assertIn('skills', response)
        self.assertIn('experience_years', response)

    @patch('anthropic.Client')
    def test_match_job(self, mock_client):
        mock_json = {
            "match_percentage": 85,
            "matching_skills": ["Python", "Django"],
            "missing_skills": ["GraphQL"],
            "recommendations": ["Highlight AWS experience"]
        }
        
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps(mock_json))]
        
        mock_instance = Mock()
        mock_instance.messages.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        response = self.handler.match_job(self.sample_cv, self.sample_job)
        self.assertIsInstance(response, dict)
        self.assertIn('match_percentage', response)
        self.assertIn('matching_skills', response)

if __name__ == '__main__':
    unittest.main()
