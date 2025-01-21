from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from agents.quality_agents.ats_validator import ATSValidator
from agents.quality_agents.cv_evaluator import CVEvaluator
from agents.quality_agents.letter_evaluator import LetterEvaluator

load_dotenv()

class Coordinator:
    def __init__(self):
        self._setup_logger()
        self.ats_validator = ATSValidator()
        self.cv_evaluator = CVEvaluator()
        self.letter_evaluator = LetterEvaluator()
        
        # Quality check weights
        self.quality_weights = {
            'ats_compliance': 0.4,
            'cv_quality': 0.4,
            'letter_quality': 0.2
        }
        
        # Minimum quality thresholds
        self.quality_thresholds = {
            'ats_compliance': 75,
            'cv_quality': 75,
            'letter_quality': 75,
            'overall_quality': 75
        }
        
        self.logger.info("Quality Coordinator initialized successfully")

    def _setup_logger(self):
        self.logger = logging.getLogger('QualityCoordinator')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/quality_coordinator_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def assess_application_quality(
        self, 
        cv_text: str, 
        letter_text: str, 
        job_description: str,
        company_name: str,
        industry: Optional[str] = None
    ) -> Dict:
        """
        Perform comprehensive quality assessment of the application
        """
        self.logger.info("Starting comprehensive quality assessment")
        try:
            # Run ATS validation
            ats_results = self.ats_validator.validate_cv(cv_text, job_description)
            
            # Run CV evaluation
            cv_results = self.cv_evaluator.evaluate_cv(cv_text, industry)
            
            # Run letter evaluation
            letter_results = self.letter_evaluator.evaluate_letter(
                letter_text, 
                job_description,
                company_name
            )
            
            # Aggregate results
            aggregated_results = self._aggregate_results(
                ats_results,
                cv_results,
                letter_results
            )
            
            # Generate comprehensive report
            quality_report = {
                'overall_quality_score': aggregated_results['overall_score'],
                'meets_quality_standards': self._check_quality_standards(aggregated_results),
                'detailed_assessment': {
                    'ats_compliance': ats_results,
                    'cv_quality': cv_results,
                    'letter_quality': letter_results
                },
                'critical_issues': self._identify_critical_issues(
                    ats_results,
                    cv_results,
                    letter_results
                ),
                'improvement_recommendations': self._generate_recommendations(
                    ats_results,
                    cv_results,
                    letter_results
                ),
                'component_scores': {
                    'ats_score': ats_results['overall_score'],
                    'cv_score': cv_results['overall_score'],
                    'letter_score': letter_results['overall_score']
                }
            }
            
            self.logger.info(f"Quality assessment completed with score: {aggregated_results['overall_score']}")
            return quality_report
            
        except Exception as e:
            self.logger.error(f"Error during quality assessment: {str(e)}")
            raise

    def _aggregate_results(self, ats_results: Dict, cv_results: Dict, letter_results: Dict) -> Dict:
        """Aggregate results from all quality checks"""
        try:
            # Calculate weighted scores
            ats_score = ats_results['overall_score'] * self.quality_weights['ats_compliance']
            cv_score = cv_results['overall_score'] * self.quality_weights['cv_quality']
            letter_score = letter_results['overall_score'] * self.quality_weights['letter_quality']
            
            # Calculate overall score
            overall_score = round(ats_score + cv_score + letter_score, 2)
            
            return {
                'overall_score': overall_score,
                'component_scores': {
                    'ats_compliance': ats_results['overall_score'],
                    'cv_quality': cv_results['overall_score'],
                    'letter_quality': letter_results['overall_score']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error aggregating results: {str(e)}")
            raise

    def _check_quality_standards(self, aggregated_results: Dict) -> Dict:
        """Check if results meet quality standards"""
        standards_check = {
            'ats_compliance': aggregated_results['component_scores']['ats_compliance'] >= 
                            self.quality_thresholds['ats_compliance'],
            'cv_quality': aggregated_results['component_scores']['cv_quality'] >= 
                         self.quality_thresholds['cv_quality'],
            'letter_quality': aggregated_results['component_scores']['letter_quality'] >= 
                            self.quality_thresholds['letter_quality'],
            'overall_quality': aggregated_results['overall_score'] >= 
                             self.quality_thresholds['overall_quality']
        }
        
        return {
            'meets_all_standards': all(standards_check.values()),
            'standards_results': standards_check
        }

    def _identify_critical_issues(
        self, 
        ats_results: Dict, 
        cv_results: Dict, 
        letter_results: Dict
    ) -> Dict:
        """Identify critical issues from all evaluations"""
        critical_issues = {
            'ats_issues': [],
            'cv_issues': [],
            'letter_issues': []
        }
        
        # ATS critical issues
        if 'critical_issues' in ats_results:
            critical_issues['ats_issues'].extend(ats_results['critical_issues'])
        
        # CV critical issues
        if 'improvement_areas' in cv_results:
            critical_issues['cv_issues'].extend(cv_results['improvement_areas'])
        
        # Letter critical issues
        if 'improvement_needed' in letter_results:
            critical_issues['letter_issues'].extend(letter_results['improvement_needed'])
        
        return critical_issues

    def _generate_recommendations(
        self, 
        ats_results: Dict, 
        cv_results: Dict, 
        letter_results: Dict
    ) -> Dict:
        """Generate comprehensive improvement recommendations"""
        recommendations = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        # Process ATS recommendations
        if ats_results['overall_score'] < self.quality_thresholds['ats_compliance']:
            recommendations['high_priority'].extend(ats_results.get('recommendations', []))
        
        # Process CV recommendations
        cv_score = cv_results['overall_score']
        if cv_score < self.quality_thresholds['cv_quality']:
            if cv_score < 60:
                recommendations['high_priority'].extend(cv_results.get('improvement_areas', []))
            else:
                recommendations['medium_priority'].extend(cv_results.get('improvement_areas', []))
        
        # Process letter recommendations
        letter_score = letter_results['overall_score']
        if letter_score < self.quality_thresholds['letter_quality']:
            if letter_score < 60:
                recommendations['high_priority'].extend(letter_results.get('improvement_needed', []))
            else:
                recommendations['medium_priority'].extend(letter_results.get('improvement_needed', []))
        
        return recommendations

    def get_quality_summary(self, quality_report: Dict) -> str:
        """Generate a human-readable quality summary"""
        try:
            summary_lines = [
                "Application Quality Assessment Summary:",
                f"Overall Quality Score: {quality_report['overall_quality_score']}/100",
                "",
                "Component Scores:",
                f"- ATS Compliance: {quality_report['component_scores']['ats_score']}/100",
                f"- CV Quality: {quality_report['component_scores']['cv_score']}/100",
                f"- Cover Letter Quality: {quality_report['component_scores']['letter_score']}/100",
                "",
                "Quality Standards:",
                f"Meets All Standards: {'Yes' if quality_report['meets_quality_standards']['meets_all_standards'] else 'No'}"
            ]
            
            # Add critical issues if any
            if any(quality_report['critical_issues'].values()):
                summary_lines.extend([
                    "",
                    "Critical Issues to Address:"
                ])
                for category, issues in quality_report['critical_issues'].items():
                    if issues:
                        summary_lines.extend([f"- {issue}" for issue in issues[:3]])
            
            # Add top recommendations
            if quality_report['improvement_recommendations']['high_priority']:
                summary_lines.extend([
                    "",
                    "Top Priority Improvements:"
                ])
                summary_lines.extend([
                    f"- {rec}" 
                    for rec in quality_report['improvement_recommendations']['high_priority'][:3]
                ])
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            self.logger.error(f"Error generating quality summary: {str(e)}")
            return "Error generating quality summary"