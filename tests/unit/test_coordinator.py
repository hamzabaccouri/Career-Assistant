import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.coordinator import Coordinator

class TestCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = Coordinator()
        
        self.sample_cv = """
        Senior Software Engineer
        
        Experience:
        - Developed Python applications using Django
        - Led team of 5 developers
        
        Skills:
        - Python, Django, React
        - AWS, Docker
        """
        
        self.sample_letter = """
        Dear Hiring Manager,
        
        I am writing to express my interest in the Senior Software Engineer position.
        With my experience in Python development and team leadership, I am confident
        in my ability to contribute to your team.
        
        Best regards,
        John Doe
        """
        
        self.sample_job = """
        Senior Software Engineer position:
        - 5+ years Python experience
        - Team leadership skills
        - Experience with cloud technologies
        """

    @patch('agents.quality_agents.ats_validator.ATSValidator.validate_cv')
    @patch('agents.quality_agents.cv_evaluator.CVEvaluator.evaluate_cv')
    @patch('agents.quality_agents.letter_evaluator.LetterEvaluator.evaluate_letter')
    def test_assess_application_quality(self, mock_letter_eval, mock_cv_eval, mock_ats_val):
        # Setup mock responses
        mock_ats_val.return_value = {
            'overall_score': 85,
            'critical_issues': [],
            'recommendations': ['Improve ATS format']
        }
        
        mock_cv_eval.return_value = {
            'overall_score': 88,
            'improvement_areas': ['Add more achievements'],
            'strengths': ['Clear experience section']
        }
        
        mock_letter_eval.return_value = {
            'overall_score': 90,
            'improvement_needed': ['Add more company specifics'],
            'strong_points': ['Professional tone']
        }
        
        # Test quality assessment
        result = self.coordinator.assess_application_quality(
            self.sample_cv,
            self.sample_letter,
            self.sample_job,
            "Tech Corp",
            "Technology"
        )
        
        # Verify result structure
        self.assertIn('overall_quality_score', result)
        self.assertIn('meets_quality_standards', result)
        self.assertIn('detailed_assessment', result)
        self.assertIn('critical_issues', result)
        self.assertIn('improvement_recommendations', result)
        
        # Verify score ranges
        self.assertGreaterEqual(result['overall_quality_score'], 0)
        self.assertLessEqual(result['overall_quality_score'], 100)

    def test_aggregate_results(self):
        ats_results = {'overall_score': 85}
        cv_results = {'overall_score': 88}
        letter_results = {'overall_score': 90}
        
        result = self.coordinator._aggregate_results(
            ats_results,
            cv_results,
            letter_results
        )
        
        self.assertIn('overall_score', result)
        self.assertIn('component_scores', result)
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)

    def test_check_quality_standards(self):
        aggregated_results = {
            'overall_score': 85,
            'component_scores': {
                'ats_compliance': 85,
                'cv_quality': 88,
                'letter_quality': 90
            }
        }
        
        result = self.coordinator._check_quality_standards(aggregated_results)
        
        self.assertIn('meets_all_standards', result)
        self.assertIn('standards_results', result)
        self.assertIsInstance(result['meets_all_standards'], bool)

    def test_identify_critical_issues(self):
        ats_results = {
            'critical_issues': ['ATS format issue']
        }
        cv_results = {
            'improvement_areas': ['Add achievements']
        }
        letter_results = {
            'improvement_needed': ['More customization']
        }
        
        issues = self.coordinator._identify_critical_issues(
            ats_results,
            cv_results,
            letter_results
        )
        
        self.assertIn('ats_issues', issues)
        self.assertIn('cv_issues', issues)
        self.assertIn('letter_issues', issues)
        self.assertTrue(any(len(issues[key]) > 0 for key in issues))

    def test_generate_recommendations(self):
        ats_results = {
            'overall_score': 65,
            'recommendations': ['Improve ATS format']
        }
        cv_results = {
            'overall_score': 70,
            'improvement_areas': ['Add achievements']
        }
        letter_results = {
            'overall_score': 75,
            'improvement_needed': ['More customization']
        }
        
        recommendations = self.coordinator._generate_recommendations(
            ats_results,
            cv_results,
            letter_results
        )
        
        self.assertIn('high_priority', recommendations)
        self.assertIn('medium_priority', recommendations)
        self.assertIn('low_priority', recommendations)

    def test_get_quality_summary(self):
        quality_report = {
            'overall_quality_score': 85,
            'meets_quality_standards': {
                'meets_all_standards': True
            },
            'component_scores': {
                'ats_score': 85,
                'cv_score': 88,
                'letter_score': 90
            },
            'critical_issues': {
                'ats_issues': [],
                'cv_issues': [],
                'letter_issues': []
            },
            'improvement_recommendations': {
                'high_priority': ['Improve ATS format'],
                'medium_priority': [],
                'low_priority': []
            }
        }
        
        summary = self.coordinator.get_quality_summary(quality_report)
        
        self.assertIsInstance(summary, str)
        self.assertIn('Quality Assessment Summary', summary)
        self.assertIn('Overall Quality Score', summary)

if __name__ == '__main__':
    unittest.main()