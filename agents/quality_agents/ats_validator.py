from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from models.model_manager import ModelManager
from utils.ats_rules import ATSRules
from agents.primary_agents.ats_optimizer import ATSOptimizer

load_dotenv()

class ATSValidator:
    def __init__(self):
        self._setup_logger()
        self.model_manager = ModelManager()
        self.ats_rules = ATSRules()
        self.ats_optimizer = ATSOptimizer()
        
        # Validation criteria weights
        self.validation_weights = {
            'format_compliance': 0.3,
            'keyword_optimization': 0.3,
            'section_structure': 0.2,
            'content_clarity': 0.2
        }
        
        self.logger.info("ATS Validator initialized successfully")

    def _setup_logger(self):
        self.logger = logging.getLogger('ATSValidator')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/ats_validator_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def validate_cv(self, cv_text: str, job_description: str) -> Dict:
        """
        Perform comprehensive ATS validation of the CV
        """
        self.logger.info("Starting ATS validation")
        try:
            # Format validation
            format_check = self._validate_format(cv_text)
            
            # Keyword validation
            keyword_check = self._validate_keywords(cv_text, job_description)
            
            # Structure validation
            structure_check = self._validate_structure(cv_text)
            
            # Content validation
            content_check = self._validate_content(cv_text, job_description)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score({
                'format': format_check,
                'keywords': keyword_check,
                'structure': structure_check,
                'content': content_check
            })
            
            validation_result = {
                'overall_score': overall_score,
                'is_ats_compliant': overall_score >= 75,
                'validation_details': {
                    'format_validation': format_check,
                    'keyword_validation': keyword_check,
                    'structure_validation': structure_check,
                    'content_validation': content_check
                },
                'critical_issues': self._identify_critical_issues({
                    'format': format_check,
                    'keywords': keyword_check,
                    'structure': structure_check,
                    'content': content_check
                }),
                'improvement_suggestions': self._generate_suggestions({
                    'format': format_check,
                    'keywords': keyword_check,
                    'structure': structure_check,
                    'content': content_check
                })
            }
            
            self.logger.info(f"Validation completed with score: {overall_score}")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error during ATS validation: {str(e)}")
            raise

    def _validate_format(self, cv_text: str) -> Dict:
        """Validate CV format compliance"""
        try:
            # Get format validation from LLM
            format_analysis = self.model_manager.get_structured_completion(
                prompt=f"Analyze the format of this CV for ATS compliance:\n\n{cv_text}",
                output_schema={
                    "is_clean_format": "boolean",
                    "has_proper_spacing": "boolean",
                    "uses_standard_sections": "boolean",
                    "formatting_issues": ["list of issues"],
                    "format_score": "number between 0 and 100"
                },
                task_type='ats_validation'
            )
            
            return {
                'score': format_analysis['format_score'],
                'issues': format_analysis['formatting_issues'],
                'passes_validation': format_analysis['is_clean_format']
            }
            
        except Exception as e:
            self.logger.error(f"Error in format validation: {str(e)}")
            return {'score': 0, 'issues': ['Validation failed'], 'passes_validation': False}

    def _validate_keywords(self, cv_text: str, job_description: str) -> Dict:
        """Validate keyword optimization"""
        try:
            # Get keyword analysis from LLM
            keyword_analysis = self.model_manager.get_structured_completion(
                prompt=f"""
                Analyze keyword optimization between CV and job description:
                
                CV:
                {cv_text}
                
                Job Description:
                {job_description}
                """,
                output_schema={
                    "keyword_matches": ["list of matched keywords"],
                    "missing_keywords": ["list of missing important keywords"],
                    "keyword_placement_score": "number between 0 and 100",
                    "optimization_level": "string"
                },
                task_type='keyword_validation'
            )
            
            return {
                'score': keyword_analysis['keyword_placement_score'],
                'matched_keywords': keyword_analysis['keyword_matches'],
                'missing_keywords': keyword_analysis['missing_keywords'],
                'passes_validation': keyword_analysis['keyword_placement_score'] >= 70
            }
            
        except Exception as e:
            self.logger.error(f"Error in keyword validation: {str(e)}")
            return {'score': 0, 'matched_keywords': [], 'missing_keywords': [], 'passes_validation': False}

    def _validate_structure(self, cv_text: str) -> Dict:
        """Validate CV structure"""
        try:
            # Use ATS rules to validate structure
            sections = cv_text.split('\n\n')
            structure_check = self.ats_rules.validate_structure(sections)
            
            return {
                'score': 100 if structure_check['valid'] else 50,
                'issues': structure_check.get('issues', []),
                'passes_validation': structure_check['valid']
            }
            
        except Exception as e:
            self.logger.error(f"Error in structure validation: {str(e)}")
            return {'score': 0, 'issues': ['Validation failed'], 'passes_validation': False}

    def _validate_content(self, cv_text: str, job_description: str) -> Dict:
        """Validate CV content quality"""
        try:
            content_analysis = self.model_manager.get_structured_completion(
                prompt=f"""
                Analyze the content quality of this CV for ATS compliance:
                
                CV:
                {cv_text}
                
                Job Description:
                {job_description}
                """,
                output_schema={
                    "content_clarity": "number between 0 and 100",
                    "bullet_point_quality": "number between 0 and 100",
                    "achievement_focus": "number between 0 and 100",
                    "content_issues": ["list of issues"]
                },
                task_type='content_validation'
            )
            
            average_score = (
                content_analysis['content_clarity'] +
                content_analysis['bullet_point_quality'] +
                content_analysis['achievement_focus']
            ) / 3
            
            return {
                'score': average_score,
                'issues': content_analysis['content_issues'],
                'passes_validation': average_score >= 70
            }
            
        except Exception as e:
            self.logger.error(f"Error in content validation: {str(e)}")
            return {'score': 0, 'issues': ['Validation failed'], 'passes_validation': False}

    def _calculate_overall_score(self, validation_results: Dict) -> float:
        """Calculate weighted overall score"""
        scores = {
            'format': validation_results['format']['score'] * self.validation_weights['format_compliance'],
            'keywords': validation_results['keywords']['score'] * self.validation_weights['keyword_optimization'],
            'structure': validation_results['structure']['score'] * self.validation_weights['section_structure'],
            'content': validation_results['content']['score'] * self.validation_weights['content_clarity']
        }
        
        return round(sum(scores.values()), 2)

    def _identify_critical_issues(self, validation_results: Dict) -> List[str]:
        """Identify critical ATS compliance issues"""
        critical_issues = []
        
        # Check format issues
        if not validation_results['format']['passes_validation']:
            critical_issues.extend(validation_results['format']['issues'])
        
        # Check keyword issues
        if not validation_results['keywords']['passes_validation']:
            critical_issues.append(
                f"Missing critical keywords: {', '.join(validation_results['keywords']['missing_keywords'][:3])}"
            )
        
        # Check structure issues
        if not validation_results['structure']['passes_validation']:
            critical_issues.extend(validation_results['structure']['issues'])
        
        # Check content issues
        if not validation_results['content']['passes_validation']:
            critical_issues.extend(validation_results['content']['issues'])
        
        return critical_issues

    def _generate_suggestions(self, validation_results: Dict) -> List[str]:
        """Generate improvement suggestions based on validation results"""
        suggestions = []
        
        # Format suggestions
        if not validation_results['format']['passes_validation']:
            suggestions.append("Improve CV formatting for better ATS readability")
        
        # Keyword suggestions
        if not validation_results['keywords']['passes_validation']:
            suggestions.append("Add missing relevant keywords from job description")
        
        # Structure suggestions
        if not validation_results['structure']['passes_validation']:
            suggestions.append("Reorganize CV sections following standard ATS format")
        
        # Content suggestions
        if not validation_results['content']['passes_validation']:
            suggestions.append("Enhance content clarity and achievement descriptions")
        
        return suggestions