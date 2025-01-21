import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.primary_agents.job_analyzer import JobAnalyzer

class TestJobAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = JobAnalyzer()
        
        self.sample_job = """
        Senior Software Engineer
        
        Requirements:
        - 5+ years of Python development experience
        - Strong knowledge of Django and React
        - Experience with AWS cloud infrastructure
        - Bachelor's degree in Computer Science or related field
        
        Responsibilities:
        - Develop and maintain web applications
        - Lead a team of junior developers
        - Collaborate with product managers
        
        Benefits:
        - Competitive salary
        - Remote work options
        - Health insurance
        """

    @patch('models.model_manager.ModelManager.get_structured_completion')
    @patch('utils.text_analyzer.TextAnalyzer.extract_keywords')
    def test_analyze_job(self, mock_extract_keywords, mock_get_structured):
        # Setup mock responses
        mock_get_structured.return_value = {
            'required_skills': ['Python', 'Django', 'React'],
            'preferred_skills': ['AWS', 'Docker'],
            'experience_required': '5+ years',
            'education_required': "Bachelor's degree",
            'responsibilities': ['Lead development team', 'Build applications'],
            'company_culture': ['Collaborative', 'Innovative'],
            'benefits': ['Remote work', 'Health insurance'],
            'job_level': 'Senior'
        }
        
        mock_extract_keywords.return_value = {
            'technical_terms': ['Python', 'Django', 'React', 'AWS'],
            'action_verbs': ['develop', 'lead', 'collaborate'],
            'nouns': ['Engineer', 'Team Lead']
        }
        
        # Test analysis
        result = self.analyzer.analyze_job(self.sample_job)
        
        # Verify result structure
        self.assertIn('requirements', result)
        self.assertIn('job_details', result)
        self.assertIn('company_culture', result)
        self.assertIn('keyword_analysis', result)
        self.assertIn('complexity_score', result)
        
        # Verify mocks were called
        mock_get_structured.assert_called_once()
        mock_extract_keywords.assert_called_once()

    def test_extract_soft_skills(self):
        text_analysis = {
            'nouns': ['Leadership', 'Communication', 'Teamwork']
        }
        llm_analysis = {
            'required_skills': ['Problem-solving', 'Analytical thinking']
        }
        
        soft_skills = self.analyzer._extract_soft_skills(text_analysis, llm_analysis)
        
        self.assertIsInstance(soft_skills, list)
        self.assertGreater(len(soft_skills), 0)

    def test_calculate_complexity_score(self):
        analysis = {
            'requirements': {
                'technical_skills': ['Python', 'Django', 'React', 'AWS'],
                'experience': 'Senior level position',
                'education': "Bachelor's degree required"
            }
        }
        
        score = self.analyzer._calculate_complexity_score(analysis)
        
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_get_required_keywords(self):
        with patch.object(self.analyzer, 'analyze_job') as mock_analyze:
            mock_analyze.return_value = {
                'requirements': {
                    'required_skills': ['Python', 'Django'],
                    'technical_skills': ['AWS', 'React']
                },
                'job_details': {
                    'responsibilities': ['Lead development team']
                }
            }
            
            keywords = self.analyzer.get_required_keywords(self.sample_job)
            
            self.assertIsInstance(keywords, list)
            self.assertGreater(len(keywords), 0)
            self.assertTrue(all(isinstance(k, str) for k in keywords))

if __name__ == '__main__':
    unittest.main()