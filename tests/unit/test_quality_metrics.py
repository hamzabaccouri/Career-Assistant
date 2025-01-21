import unittest
from unittest.mock import patch, MagicMock, call
import logging
import os
from datetime import datetime
from core.quality_metrics import QualityMetrics

class TestQualityMetrics(unittest.TestCase):
    @patch('logging.getLogger')
    @patch('logging.FileHandler')
    def setUp(self, mock_file_handler, mock_get_logger):
        # Setup logger mocking
        self.mock_logger = MagicMock()
        mock_get_logger.return_value = self.mock_logger
        
        # Initialize QualityMetrics with mocked logger
        self.metrics = QualityMetrics()
        
        # Sample test data with complete metrics
        self.cv_metrics = {
            'content_relevance': 85,
            'skills_match': 90,
            'experience_quality': 80,
            'format_compliance': 95
        }
        
        self.letter_metrics = {
            'customization': 88,
            'content_relevance': 85,
            'professional_tone': 90,
            'formatting': 92
        }
        
        self.ats_metrics = {
            'keyword_optimization': 87,
            'format_compliance': 85,
            'section_structure': 88,
            'content_clarity': 90
        }

    def test_calculate_cv_score_invalid_input(self):
        """Test CV score calculation with invalid input"""
        # Test with None
        with self.assertRaises(Exception):
            self.metrics.calculate_cv_score(None)
            
        # Test with missing required metrics
        result = self.metrics.calculate_cv_score({})
        self.assertEqual(result['total_score'], 0)
        self.assertFalse(result['meets_threshold'])

        # Test with incorrect metric keys
        invalid_metrics = {'invalid_key': 100}
        result = self.metrics.calculate_cv_score(invalid_metrics)
        self.assertEqual(result['total_score'], 0)
        self.assertFalse(result['meets_threshold'])

    def test_calculate_letter_score_invalid_input(self):
        """Test letter score calculation with invalid input"""
        # Test with None
        with self.assertRaises(Exception):
            self.metrics.calculate_letter_score(None)
            
        # Test with missing required metrics
        result = self.metrics.calculate_letter_score({})
        self.assertEqual(result['total_score'], 0)
        self.assertFalse(result['meets_threshold'])

        # Test with incorrect metric keys
        invalid_metrics = {'invalid_key': 100}
        result = self.metrics.calculate_letter_score(invalid_metrics)
        self.assertEqual(result['total_score'], 0)
        self.assertFalse(result['meets_threshold'])

    def test_calculate_ats_score_invalid_input(self):
        """Test ATS score calculation with invalid input"""
        # Test with None
        with self.assertRaises(Exception):
            self.metrics.calculate_ats_score(None)
            
        # Test with missing required metrics
        result = self.metrics.calculate_ats_score({})
        self.assertEqual(result['total_score'], 0)
        self.assertFalse(result['meets_threshold'])

        # Test with incorrect metric keys
        invalid_metrics = {'invalid_key': 100}
        result = self.metrics.calculate_ats_score(invalid_metrics)
        self.assertEqual(result['total_score'], 0)
        self.assertFalse(result['meets_threshold'])

    def test_calculate_cv_score_valid_input(self):
        """Test CV score calculation with valid input"""
        result = self.metrics.calculate_cv_score(self.cv_metrics)
        expected_score = (
            85 * 0.3 +   # content_relevance
            90 * 0.25 +  # skills_match
            80 * 0.25 +  # experience_quality
            95 * 0.2     # format_compliance
        )
        self.assertAlmostEqual(result['total_score'], round(expected_score, 2))

    def test_calculate_letter_score_valid_input(self):
        """Test letter score calculation with valid input"""
        result = self.metrics.calculate_letter_score(self.letter_metrics)
        expected_score = (
            88 * 0.3 +  # customization
            85 * 0.3 +  # content_relevance
            90 * 0.2 +  # professional_tone
            92 * 0.2    # formatting
        )
        self.assertAlmostEqual(result['total_score'], round(expected_score, 2))

    def test_calculate_ats_score_valid_input(self):
        """Test ATS score calculation with valid input"""
        result = self.metrics.calculate_ats_score(self.ats_metrics)
        expected_score = (
            87 * 0.3 +  # keyword_optimization
            85 * 0.3 +  # format_compliance
            88 * 0.2 +  # section_structure
            90 * 0.2    # content_clarity
        )
        self.assertAlmostEqual(result['total_score'], round(expected_score, 2))

    def test_calculate_overall_quality(self):
        """Test overall quality calculation"""
        result = self.metrics.calculate_overall_quality(85, 88, 87)
        expected_score = 85 * 0.4 + 88 * 0.3 + 87 * 0.3
        self.assertAlmostEqual(result['overall_score'], round(expected_score, 2))

    def test_get_quality_assessment(self):
        """Test comprehensive quality assessment"""
        result = self.metrics.get_quality_assessment(
            self.cv_metrics,
            self.letter_metrics,
            self.ats_metrics
        )
        self.assertIn('overall_quality', result)
        self.assertIn('cv_assessment', result)
        self.assertIn('letter_assessment', result)
        self.assertIn('ats_assessment', result)
        self.assertIn('meets_all_thresholds', result)

    def test_get_improvement_priorities(self):
        """Test improvement priorities identification"""
        failed_assessment = {
            'cv_assessment': {
                'meets_threshold': False,
                'component_scores': {
                    'content_score': 60,
                    'skills_score': 70,
                    'experience_score': 65,
                    'format_score': 75
                }
            },
            'letter_assessment': {
                'meets_threshold': True,
                'component_scores': {
                    'customization_score': 80,
                    'content_score': 85,
                    'tone_score': 82,
                    'format_score': 88
                }
            },
            'ats_assessment': {
                'meets_threshold': False,
                'component_scores': {
                    'keyword_score': 65,
                    'format_score': 70,
                    'structure_score': 72,
                    'clarity_score': 68
                }
            }
        }
        
        priorities = self.metrics.get_improvement_priorities(failed_assessment)
        self.assertIsInstance(priorities, list)
        self.assertTrue(any('CV content' in priority for priority in priorities))
        self.assertTrue(any('ATS keyword' in priority for priority in priorities))

    @patch('logging.getLogger')
    @patch('logging.FileHandler')
    def test_logger_setup(self, mock_file_handler, mock_get_logger):
        """Test logger setup"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        metrics = QualityMetrics()
        
        # Verify logger configuration
        mock_get_logger.assert_called_once_with('QualityMetrics')
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_logger.addHandler.assert_called()

if __name__ == '__main__':
    unittest.main()