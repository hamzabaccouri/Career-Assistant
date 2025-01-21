import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from datetime import datetime
import json
from core.workflow_manager import WorkflowManager

class TestWorkflowManager(unittest.TestCase):
    @patch('logging.getLogger')
    @patch('logging.FileHandler')
    def setUp(self, mock_file_handler, mock_get_logger):
        # Setup logger mocking
        self.mock_logger = MagicMock()
        mock_get_logger.return_value = self.mock_logger
        
        # Initialize WorkflowManager
        self.workflow_manager = WorkflowManager()
        
        # Sample test data
        self.cv_file_path = "test_cv.pdf"
        self.job_description = "Software Engineer position with 5+ years experience..."
        self.company_name = "Tech Corp"
        
        # Mock successful component results
        self.mock_cv_analysis = {
            'skills': ['Python', 'Java'],
            'experience': '5 years',
            'education': 'Masters'
        }
        
        self.mock_job_analysis = {
            'required_skills': ['Python', 'Java'],
            'experience_needed': '5 years',
            'education_required': 'Bachelor'
        }
        
        self.mock_optimization_result = {
            'optimized_cv': 'Optimized CV content...',
            'recommendations': ['Add more keywords']
        }
        
        self.mock_quality_report = {
            'component_scores': {
                'cv_score': 85,
                'ats_score': 90,
                'letter_score': 88
            },
            'improvement_recommendations': {
                'high_priority': ['Improve skills section'],
                'medium_priority': ['Add more achievements']
            }
        }

    def test_initialization(self):
        """Test proper initialization of WorkflowManager"""
        self.assertIsNotNone(self.workflow_manager.document_processor)
        self.assertIsNotNone(self.workflow_manager.cv_analyzer)
        self.assertIsNotNone(self.workflow_manager.job_analyzer)
        self.assertFalse(any(self.workflow_manager.workflow_states.values()))

    @patch('os.path.exists')
    def test_validate_inputs_success(self, mock_exists):
        """Test input validation with valid inputs"""
        mock_exists.return_value = True
        
        is_valid, error = self.workflow_manager.validate_inputs(
            self.cv_file_path,
            self.job_description,
            self.company_name
        )
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    @patch('os.path.exists')
    def test_validate_inputs_failure(self, mock_exists):
        """Test input validation with invalid inputs"""
        # Test 1: Invalid file format
        mock_exists.return_value = True  # File exists but wrong format
        is_valid, error = self.workflow_manager.validate_inputs(
            "test.txt",
            self.job_description,
            self.company_name
        )
        self.assertFalse(is_valid)
        self.assertIn("Unsupported CV format", error)

        # Test 2: Non-existent file
        mock_exists.return_value = False
        is_valid, error = self.workflow_manager.validate_inputs(
            self.cv_file_path,
            self.job_description,
            self.company_name
        )
        self.assertFalse(is_valid)
        self.assertIn("file does not exist", error)
        
        # Test 3: Short job description
        mock_exists.return_value = True  # Reset exists to True
        is_valid, error = self.workflow_manager.validate_inputs(
            "test.pdf",
            "Too short",
            self.company_name
        )
        self.assertFalse(is_valid)
        self.assertIn("description is too short", error)
        
        # Test 4: Empty company name
        is_valid, error = self.workflow_manager.validate_inputs(
            "test.pdf",
            self.job_description,
            ""
        )
        self.assertFalse(is_valid)
        self.assertIn("Invalid company name", error)

    @patch('os.path.exists')
    def test_process_application_success(self, mock_exists):
        """Test successful application processing workflow"""
        mock_exists.return_value = True
        
        # Mock all component methods
        self.workflow_manager.document_processor.process_document = MagicMock(
            return_value={'success': True, 'content': 'CV content...'}
        )
        self.workflow_manager.cv_analyzer.analyze_cv = MagicMock(
            return_value=self.mock_cv_analysis
        )
        self.workflow_manager.job_analyzer.analyze_job = MagicMock(
            return_value=self.mock_job_analysis
        )
        self.workflow_manager.cv_matcher.match_cv_to_job = MagicMock(
            return_value={'overall_match': {'score': 85}}
        )
        self.workflow_manager.ats_optimizer.optimize_cv = MagicMock(
            return_value=self.mock_optimization_result
        )
        self.workflow_manager.letter_writer.generate_cover_letter = MagicMock(
            return_value={'letter': 'Cover letter content...'}
        )
        self.workflow_manager.coordinator.assess_application_quality = MagicMock(
            return_value=self.mock_quality_report
        )
        
        # Process application
        result = self.workflow_manager.process_application(
            self.cv_file_path,
            self.job_description,
            self.company_name
        )
        
        # Verify workflow states
        self.assertTrue(all(self.workflow_manager.workflow_states.values()))
        
        # Verify result structure
        self.assertIn('original_cv', result)
        self.assertIn('job_analysis', result)
        self.assertIn('optimized_application', result)
        self.assertIn('quality_assessment', result)
        
        # Verify component calls
        self.workflow_manager.document_processor.process_document.assert_called_once()
        self.workflow_manager.cv_analyzer.analyze_cv.assert_called_once()
        self.workflow_manager.job_analyzer.analyze_job.assert_called_once()

    def test_process_application_failure(self):
        """Test application processing with document processing failure"""
        self.workflow_manager.document_processor.process_document = MagicMock(
            return_value={'success': False, 'error': 'Processing failed'}
        )
        
        with self.assertRaises(ValueError):
            self.workflow_manager.process_application(
                self.cv_file_path,
                self.job_description,
                self.company_name
            )
        
        self.assertFalse(self.workflow_manager.workflow_states['document_processing'])

    def test_get_workflow_status(self):
        """Test workflow status reporting"""
        status = self.workflow_manager.get_workflow_status()
        
        self.assertIn('completed_steps', status)
        self.assertIn('total_steps', status)
        self.assertIn('completion_percentage', status)
        self.assertIn('step_status', status)
        
        # Test initial state
        self.assertEqual(status['completed_steps'], 0)
        self.assertEqual(status['total_steps'], len(self.workflow_manager.workflow_states))
        self.assertEqual(status['completion_percentage'], 0)

    def test_get_application_summary(self):
        """Test application summary generation"""
        mock_results = {
            'initial_match': {'overall_match': {'score': 85}},
            'quality_assessment': {
                'component_scores': {
                    'ats_score': 90,
                    'cv_score': 88,
                    'letter_score': 85
                },
                'critical_issues': {
                    'cv': ['Missing key skills']
                }
            },
            'optimized_application': {
                'cover_letter': 'Letter content...'
            },
            'workflow_status': {
                'completed_steps': 5,
                'total_steps': 5,
                'completion_percentage': 100
            }
        }
        
        summary = self.workflow_manager.get_application_summary(mock_results)
        
        self.assertIn("Application Processing Summary", summary)
        self.assertIn("Initial Match Score: 85/100", summary)
        self.assertIn("Missing key skills", summary)

    def test_get_improvement_recommendations(self):
        """Test improvement recommendations extraction"""
        mock_results = {
            'quality_assessment': {
                'improvement_recommendations': {
                    'high_priority': ['Improve skills section'],
                    'medium_priority': ['Add more achievements']
                }
            },
            'optimized_application': {
                'optimization_details': {
                    'recommendations': ['Add more keywords']
                }
            }
        }
        
        recommendations = self.workflow_manager.get_improvement_recommendations(mock_results)
        
        self.assertTrue(any('High Priority' in rec for rec in recommendations))
        self.assertTrue(any('Medium Priority' in rec for rec in recommendations))
        self.assertTrue(any('Optimization' in rec for rec in recommendations))

    def test_reset_workflow_states(self):
        """Test workflow state reset"""
        # Set some states to True
        self.workflow_manager.workflow_states['document_processing'] = True
        self.workflow_manager.workflow_states['initial_analysis'] = True
        
        # Reset states
        self.workflow_manager._reset_workflow_states()
        
        # Verify all states are False
        self.assertFalse(any(self.workflow_manager.workflow_states.values()))

if __name__ == '__main__':
    unittest.main()