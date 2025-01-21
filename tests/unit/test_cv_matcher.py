import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.primary_agents.cv_matcher import CVMatcher

class TestCVMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = CVMatcher()
        
        self.sample_cv = """
        Senior Software Engineer
        
        Experience:
        - 5 years developing Python applications using Django
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

    @patch('agents.primary_agents.cv_analyzer.CVAnalyzer.analyze_cv')
    @patch('agents.primary_agents.job_analyzer.JobAnalyzer.analyze_job')
    def test_match_cv_to_job(self, mock_job_analyze, mock_cv_analyze):
        # Setup mock responses
        mock_cv_analyze.return_value = {
            'skills': {
                'technical_skills': ['Python', 'Django', 'React']
            },
            'experience': {
                'years': 5
            },
            'education': "Bachelor's degree",
            'ats_compliance': {
                'format_score': 90
            }
        }
        
        mock_job_analyze.return_value = {
            'requirements': {
                'required_skills': ['Python', 'Django'],
                'preferred_skills': ['React', 'AWS'],
                'experience': '5+ years',
                'education': "Bachelor's degree"
            }
        }
        
        # Test matching
        result = self.matcher.match_cv_to_job(self.sample_cv, self.sample_job)
        
        # Verify result structure
        self.assertIn('overall_match', result)
        self.assertIn('skills_match', result)
        self.assertIn('experience_match', result)
        self.assertIn('education_match', result)
        self.assertIn('recommendations', result)
        
        # Verify score ranges
        self.assertGreaterEqual(result['overall_match']['score'], 0)
        self.assertLessEqual(result['overall_match']['score'], 100)

    def test_calculate_skills_match(self):
        cv_analysis = {
            'skills': {
                'technical_skills': ['Python', 'Django', 'React']
            }
        }
        
        job_analysis = {
            'requirements': {
                'required_skills': ['Python', 'Django'],
                'preferred_skills': ['React', 'AWS']
            }
        }
        
        result = self.matcher._calculate_skills_match(cv_analysis, job_analysis)
        
        self.assertIsInstance(result['score'], float)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        self.assertIn('missing_required', result)
        self.assertIn('missing_preferred', result)

    def test_get_match_level(self):
        self.assertEqual(self.matcher._get_match_level(95), "Excellent Match")
        self.assertEqual(self.matcher._get_match_level(80), "Strong Match")
        self.assertEqual(self.matcher._get_match_level(65), "Good Match")
        self.assertEqual(self.matcher._get_match_level(45), "Partial Match")
        self.assertEqual(self.matcher._get_match_level(30), "Low Match")

    def test_generate_recommendations(self):
        cv_analysis = {
            'experience': {'years': 3},
            'ats_compliance': {'format_score': 70}
        }
        
        job_analysis = {
            'requirements': {'experience_years': 5}
        }
        
        skills_match = {
            'missing_required': ['AWS'],
            'missing_preferred': ['Docker']
        }
        
        recommendations = self.matcher._generate_recommendations(
            cv_analysis, job_analysis, skills_match
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(all(isinstance(r, str) for r in recommendations))

if __name__ == '__main__':
    unittest.main()