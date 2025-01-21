# tests/unit/test_ats_optimizer.py
import unittest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import json

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.primary_agents.ats_optimizer import ATSOptimizer

class TestATSOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = ATSOptimizer()
        
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

    @patch('agents.primary_agents.cv_matcher.CVMatcher.match_cv_to_job')
    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_optimize_cv(self, mock_get_structured, mock_match):
        # Setup mock responses
        mock_match.return_value = {
            'overall_match': {'score': 75}
        }
        
        mock_get_structured.return_value = {
            'optimized_text': 'Optimized CV content',
            'changes': ['Added keywords', 'Restructured sections'],
            'format_suggestions': ['Use bullet points', 'Add section headers'],
            'recommendations': ['Add more quantifiable achievements']
        }
        
        # Test optimization
        result = self.optimizer.optimize_cv(self.sample_cv, self.sample_job)
        
        # Verify result structure
        self.assertIn('optimized_cv', result)
        self.assertIn('improvements', result)
        self.assertIn('optimization_details', result)
        self.assertIn('recommendations', result)

    @patch('models.model_manager.ModelManager.get_structured_completion')
    def test_get_llm_optimization(self, mock_get_structured):
        mock_get_structured.return_value = {
            'optimized_text': 'Optimized CV content',
            'changes': ['Added keywords', 'Restructured sections'],
            'format_suggestions': ['Use bullet points'],
            'recommendations': ['Add more details']
        }
        
        result = self.optimizer._get_llm_optimization(
            self.sample_cv,
            self.sample_job,
            75.0
        )
        
        self.assertIn('optimized_text', result)
        self.assertIn('changes', result)
        self.assertIn('format_suggestions', result)

    def test_calculate_improvements(self):
        optimization_content = {
            'changes': ['Change 1', 'Change 2'],
            'format_suggestions': ['Suggestion 1']
        }
        
        result = self.optimizer._calculate_improvements(
            optimization_content,
            initial_score=75.0,
            final_score=85.0
        )
        
        self.assertIn('score_improvement', result)
        self.assertIn('changes_made', result)
        self.assertIn('has_significant_improvement', result)

    @patch('utils.ats_rules.ATSRules.validate_structure')
    @patch('agents.primary_agents.cv_matcher.CVMatcher.match_cv_to_job')
    def test_validate_optimization(self, mock_match, mock_validate):
        mock_validate.return_value = {
            'valid': True,
            'issues': []
        }
        
        mock_match.return_value = {
            'overall_match': {
                'score': 85
            }
        }
        
        result = self.optimizer.validate_optimization(
            self.sample_cv,
            self.sample_job
        )
        
        self.assertIn('is_ats_compliant', result)
        self.assertIn('match_score', result)
        self.assertIn('compliance_issues', result)
        self.assertIn('successful_optimization', result)

if __name__ == '__main__':
    unittest.main()