from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from agents.coordinator import Coordinator
from agents.primary_agents.cv_analyzer import CVAnalyzer
from agents.primary_agents.job_analyzer import JobAnalyzer
from agents.primary_agents.ats_optimizer import ATSOptimizer
from agents.primary_agents.cv_matcher import CVMatcher
from agents.primary_agents.letter_writer import LetterWriter
from utils.document_processor import DocumentProcessor

load_dotenv()

class WorkflowManager:
    def __init__(self):
        self._setup_logger()
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.cv_analyzer = CVAnalyzer()
        self.job_analyzer = JobAnalyzer()
        self.ats_optimizer = ATSOptimizer()
        self.cv_matcher = CVMatcher()
        self.letter_writer = LetterWriter()
        self.coordinator = Coordinator()
        
        # Workflow states
        self.workflow_states = {
            'document_processing': False,
            'initial_analysis': False,
            'optimization': False,
            'letter_generation': False,
            'quality_check': False
        }
        
        self.logger.info("Workflow Manager initialized successfully")

    def _setup_logger(self):
        """Configure logging"""
        self.logger = logging.getLogger('WorkflowManager')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/workflow_manager_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def process_application(
        self,
        cv_file_path: str,
        job_description: str,
        company_name: str,
        industry: Optional[str] = None,
        generate_letter: bool = True
    ) -> Dict:
        """
        Process complete job application workflow
        """
        self.logger.info("Starting application processing workflow")
        try:
            # Reset workflow states
            self._reset_workflow_states()
            
            # Process CV document
            cv_result = self.document_processor.process_document(cv_file_path)
            if not cv_result['success']:
                raise ValueError(f"Failed to process CV: {cv_result['error']}")
            
            cv_text = cv_result['content']
            self.workflow_states['document_processing'] = True
            
            # Initial analysis
            cv_analysis = self.cv_analyzer.analyze_cv(cv_text)
            job_analysis = self.job_analyzer.analyze_job(job_description)
            initial_match = self.cv_matcher.match_cv_to_job(cv_text, job_description)
            self.workflow_states['initial_analysis'] = True
            
            # Optimize CV
            optimization_result = self.ats_optimizer.optimize_cv(cv_text, job_description)
            optimized_cv = optimization_result['optimized_cv']
            self.workflow_states['optimization'] = True
            
            # Generate cover letter if requested
            letter_text = None
            if generate_letter:
                letter_result = self.letter_writer.generate_cover_letter(
                    optimized_cv,
                    job_description,
                    company_name
                )
                letter_text = letter_result['letter']
                self.workflow_states['letter_generation'] = True
            
            # Quality assessment
            quality_report = self.coordinator.assess_application_quality(
                optimized_cv,
                letter_text if letter_text else "",
                job_description,
                company_name,
                industry
            )
            self.workflow_states['quality_check'] = True
            
            # Prepare final results
            final_results = {
                'original_cv': {
                    'content': cv_text,
                    'analysis': cv_analysis
                },
                'job_analysis': job_analysis,
                'initial_match': initial_match,
                'optimized_application': {
                    'cv': optimized_cv,
                    'optimization_details': optimization_result,
                    'cover_letter': letter_text if letter_text else None
                },
                'quality_assessment': quality_report,
                'workflow_status': self.get_workflow_status()
            }
            
            self.logger.info("Application processing workflow completed successfully")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error in application processing workflow: {str(e)}")
            raise

    def _reset_workflow_states(self):
        """Reset all workflow states to False"""
        for state in self.workflow_states:
            self.workflow_states[state] = False

    def get_workflow_status(self) -> Dict:
        """Get current workflow status"""
        completed_steps = sum(1 for state in self.workflow_states.values() if state)
        total_steps = len(self.workflow_states)
        
        return {
            'completed_steps': completed_steps,
            'total_steps': total_steps,
            'completion_percentage': round((completed_steps / total_steps) * 100, 2),
            'step_status': {
                step: {
                    'completed': status,
                    'order': idx + 1
                }
                for idx, (step, status) in enumerate(self.workflow_states.items())
            }
        }

    def validate_inputs(
        self,
        cv_file_path: str,
        job_description: str,
        company_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate workflow inputs"""
        try:
            # Check CV file
            if not os.path.exists(cv_file_path):
                return False, "CV file does not exist"
            
            # Validate file format
            valid_formats = {'.pdf', '.docx', '.doc'}
            file_ext = os.path.splitext(cv_file_path)[1].lower()
            if file_ext not in valid_formats:
                return False, f"Unsupported CV format: {file_ext}"
            
            # Check job description
            if not job_description or len(job_description.strip()) < 50:
                return False, "Job description is too short or empty"
            
            # Check company name
            if not company_name or len(company_name.strip()) < 2:
                return False, "Invalid company name"
            
            return True, None
            
        except Exception as e:
            self.logger.error(f"Error validating inputs: {str(e)}")
            return False, str(e)

    def get_application_summary(self, results: Dict) -> str:
        """Generate human-readable application summary"""
        try:
            summary_lines = [
                "Application Processing Summary:",
                "-" * 30,
                f"Initial Match Score: {results['initial_match']['overall_match']['score']}/100",
                "",
                "Optimization Results:",
                f"- ATS Compliance Score: {results['quality_assessment']['component_scores']['ats_score']}/100",
                f"- CV Quality Score: {results['quality_assessment']['component_scores']['cv_score']}/100"
            ]
            
            if results['optimized_application']['cover_letter']:
                summary_lines.append(
                    f"- Cover Letter Score: {results['quality_assessment']['component_scores']['letter_score']}/100"
                )
            
            summary_lines.extend([
                "",
                "Workflow Status:",
                f"- Completed Steps: {results['workflow_status']['completed_steps']}/{results['workflow_status']['total_steps']}",
                f"- Completion: {results['workflow_status']['completion_percentage']}%"
            ])
            
            # Add critical issues if any
            if results['quality_assessment'].get('critical_issues'):
                summary_lines.extend([
                    "",
                    "Critical Issues to Address:"
                ])
                for category, issues in results['quality_assessment']['critical_issues'].items():
                    if issues:
                        summary_lines.extend([f"- {issue}" for issue in issues[:3]])
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            self.logger.error(f"Error generating application summary: {str(e)}")
            return "Error generating application summary"

    def get_improvement_recommendations(self, results: Dict) -> List[str]:
        """Extract prioritized improvement recommendations"""
        try:
            recommendations = []
            
            # Get quality assessment recommendations
            if 'improvement_recommendations' in results['quality_assessment']:
                quality_recs = results['quality_assessment']['improvement_recommendations']
                
                # High priority recommendations
                if quality_recs.get('high_priority'):
                    recommendations.extend([
                        f"[High Priority] {rec}"
                        for rec in quality_recs['high_priority']
                    ])
                
                # Medium priority recommendations
                if quality_recs.get('medium_priority'):
                    recommendations.extend([
                        f"[Medium Priority] {rec}"
                        for rec in quality_recs['medium_priority']
                    ])
            
            # Get optimization recommendations
            if 'optimization_details' in results['optimized_application']:
                opt_details = results['optimized_application']['optimization_details']
                if 'recommendations' in opt_details:
                    recommendations.extend([
                        f"[Optimization] {rec}"
                        for rec in opt_details['recommendations']
                    ])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting improvement recommendations: {str(e)}")
            return ["Error retrieving recommendations"]