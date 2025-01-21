# tests/unit/test_model_manager.py
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

from models.model_manager import ModelManager

class TestModelManager(unittest.TestCase):
    def setUp(self):
        self.manager = ModelManager()
        
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

    def test_initialization(self):
        self.assertIsNotNone(self.manager.openai_handler)
        self.assertIsNotNone(self.manager.anthropic_handler)

    @patch('models.openai_handler.OpenAIHandler.get_completion')
    def test_get_completion_openai(self, mock_openai):
        mock_openai.return_value = "OpenAI response"
        response = self.manager.get_completion("Test prompt", preferred_service='openai')
        self.assertEqual(response, "OpenAI response")
        mock_openai.assert_called_once()

    @patch('models.anthropic_handler.AnthropicHandler.get_completion')
    def test_get_completion_anthropic(self, mock_anthropic):
        mock_anthropic.return_value = "Anthropic response"
        response = self.manager.get_completion("Test prompt", preferred_service='anthropic')
        self.assertEqual(response, "Anthropic response")
        mock_anthropic.assert_called_once()

    @patch('models.openai_handler.OpenAIHandler.get_completion')
    @patch('models.anthropic_handler.AnthropicHandler.get_completion')
    def test_fallback_mechanism(self, mock_anthropic, mock_openai):
        mock_openai.side_effect = Exception("OpenAI error")
        mock_anthropic.return_value = "Fallback response"
        
        response = self.manager.get_completion("Test prompt", preferred_service='openai')
        self.assertEqual(response, "Fallback response")
        mock_openai.assert_called_once()
        mock_anthropic.assert_called_once()

    @patch('models.anthropic_handler.AnthropicHandler.get_structured_completion')
    def test_analyze_cv(self, mock_analyze):
        mock_response = {
            "skills": ["Python", "Django"],
            "experience_years": 5,
            "key_achievements": ["Led team"],
            "missing_elements": ["Certifications"],
            "improvement_suggestions": ["Add more details"]
        }
        mock_analyze.return_value = mock_response
        
        response = self.manager.analyze_cv(self.sample_cv)
        self.assertEqual(response, mock_response)
        mock_analyze.assert_called_once()

    @patch('models.openai_handler.OpenAIHandler.get_structured_completion')
    def test_match_job(self, mock_match):
        mock_response = {
            "match_percentage": 85,
            "matching_skills": ["Python", "Django"],
            "missing_skills": ["GraphQL"],
            "recommendations": ["Highlight AWS experience"]
        }
        mock_match.return_value = mock_response
        
        response = self.manager.match_job(self.sample_cv, self.sample_job)
        self.assertEqual(response, mock_response)
        mock_match.assert_called_once()

if __name__ == '__main__':
    unittest.main()