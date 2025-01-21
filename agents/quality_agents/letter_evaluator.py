from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from models.model_manager import ModelManager
from agents.primary_agents.letter_writer import LetterWriter

load_dotenv()

class LetterEvaluator:
    def __init__(self):
        self._setup_logger()
        self.model_manager = ModelManager()
        self.letter_writer = LetterWriter()
        
        # Evaluation criteria weights
        self.evaluation_weights = {
            'content_relevance': 0.25,
            'professional_tone': 0.25,
            'customization': 0.25,
            'structure_format': 0.25
        }
        
        # Minimum acceptable scores
        self.minimum_scores = {
            'content_relevance': 70,
            'professional_tone': 75,
            'customization': 70,
            'structure_format': 75
        }
        
        self.logger.info("Letter Evaluator initialized successfully")

    def _setup_logger(self):
        self.logger = logging.getLogger('LetterEvaluator')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/letter_evaluator_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def evaluate_letter(self, letter_text: str, job_description: str, company_name: str) -> Dict:
        """Evaluate cover letter quality and effectiveness"""
        self.logger.info("Starting cover letter evaluation")
        try:
            # Evaluate content relevance
            content_eval = self._evaluate_content_relevance(letter_text, job_description)
            
            # Evaluate professional tone
            tone_eval = self._evaluate_professional_tone(letter_text)
            
            # Evaluate customization
            custom_eval = self._evaluate_customization(letter_text, job_description, company_name)
            
            # Evaluate structure and format
            format_eval = self._evaluate_structure_format(letter_text)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score({
                'content': content_eval,
                'tone': tone_eval,
                'customization': custom_eval,
                'format': format_eval
            })
            
            evaluation_result = {
                'overall_score': overall_score,
                'evaluation_summary': {
                    'content_relevance': content_eval,
                    'professional_tone': tone_eval,
                    'customization_level': custom_eval,
                    'structure_quality': format_eval
                },
                'meets_standards': self._check_minimum_standards({
                    'content_relevance': content_eval['score'],
                    'professional_tone': tone_eval['score'],
                    'customization': custom_eval['score'],
                    'structure_format': format_eval['score']
                }),
                'strong_points': self._identify_strengths({
                    'content': content_eval,
                    'tone': tone_eval,
                    'custom': custom_eval,
                    'format': format_eval
                }),
                'improvement_needed': self._identify_improvements({
                    'content': content_eval,
                    'tone': tone_eval,
                    'custom': custom_eval,
                    'format': format_eval
                })
            }
            
            self.logger.info(f"Evaluation completed with score: {overall_score}")
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"Error during letter evaluation: {str(e)}")
            raise

    def _evaluate_content_relevance(self, letter_text: str, job_description: str) -> Dict:
        """Evaluate content relevance to job requirements"""
        try:
            relevance_analysis = self.model_manager.get_structured_completion(
                prompt=f"""
                Evaluate how well this cover letter addresses the job requirements:
                
                Cover Letter:
                {letter_text}
                
                Job Description:
                {job_description}
                """,
                output_schema={
                    "relevance_score": "number between 0 and 100",
                    "key_requirements_addressed": ["list of addressed requirements"],
                    "missing_requirements": ["list of missing requirements"],
                    "effectiveness": "number between 0 and 100"
                },
                task_type='content_evaluation'
            )
            
            score = (relevance_analysis['relevance_score'] + relevance_analysis['effectiveness']) / 2
            
            return {
                'score': score,
                'addressed_requirements': relevance_analysis['key_requirements_addressed'],
                'missing_requirements': relevance_analysis['missing_requirements']
            }
            
        except Exception as e:
            self.logger.error(f"Error in content evaluation: {str(e)}")
            return {'score': 0, 'addressed_requirements': [], 'missing_requirements': []}

    def _evaluate_professional_tone(self, letter_text: str) -> Dict:
        """Evaluate professional tone and language"""
        try:
            tone_analysis = self.model_manager.get_structured_completion(
                prompt=f"Evaluate the professional tone of this cover letter:\n\n{letter_text}",
                output_schema={
                    "tone_score": "number between 0 and 100",
                    "language_quality": "number between 0 and 100",
                    "professionalism_issues": ["list of issues"],
                    "strong_elements": ["list of strong elements"]
                },
                task_type='tone_evaluation'
            )
            
            score = (tone_analysis['tone_score'] + tone_analysis['language_quality']) / 2
            
            return {
                'score': score,
                'issues': tone_analysis['professionalism_issues'],
                'strengths': tone_analysis['strong_elements']
            }
            
        except Exception as e:
            self.logger.error(f"Error in tone evaluation: {str(e)}")
            return {'score': 0, 'issues': [], 'strengths': []}

    def _evaluate_customization(self, letter_text: str, job_description: str, company_name: str) -> Dict:
        """Evaluate level of customization"""
        try:
            custom_analysis = self.model_manager.get_structured_completion(
                prompt=f"""
                Evaluate how well this cover letter is customized:
                
                Cover Letter:
                {letter_text}
                
                Job Description:
                {job_description}
                
                Company:
                {company_name}
                """,
                output_schema={
                    "customization_score": "number between 0 and 100",
                    "company_specific_content": ["list of company-specific elements"],
                    "generic_elements": ["list of generic elements"],
                    "personalization_level": "number between 0 and 100"
                },
                task_type='customization_evaluation'
            )
            
            score = (
                custom_analysis['customization_score'] + 
                custom_analysis['personalization_level']
            ) / 2
            
            return {
                'score': score,
                'company_specific': custom_analysis['company_specific_content'],
                'generic_elements': custom_analysis['generic_elements']
            }
            
        except Exception as e:
            self.logger.error(f"Error in customization evaluation: {str(e)}")
            return {'score': 0, 'company_specific': [], 'generic_elements': []}

    def _evaluate_structure_format(self, letter_text: str) -> Dict:
        """Evaluate letter structure and format"""
        try:
            format_analysis = self.model_manager.get_structured_completion(
                prompt=f"Evaluate the structure and format of this cover letter:\n\n{letter_text}",
                output_schema={
                    "structure_score": "number between 0 and 100",
                    "formatting_score": "number between 0 and 100",
                    "structure_issues": ["list of structural issues"],
                    "format_strengths": ["list of format strengths"]
                },
                task_type='format_evaluation'
            )
            
            score = (format_analysis['structure_score'] + format_analysis['formatting_score']) / 2
            
            return {
                'score': score,
                'issues': format_analysis['structure_issues'],
                'strengths': format_analysis['format_strengths']
            }
            
        except Exception as e:
            self.logger.error(f"Error in structure evaluation: {str(e)}")
            return {'score': 0, 'issues': [], 'strengths': []}

    def _calculate_overall_score(self, evaluation_results: Dict) -> float:
        """Calculate weighted overall score"""
        scores = {
            'content': evaluation_results['content']['score'] * self.evaluation_weights['content_relevance'],
            'tone': evaluation_results['tone']['score'] * self.evaluation_weights['professional_tone'],
            'customization': evaluation_results['customization']['score'] * self.evaluation_weights['customization'],
            'format': evaluation_results['format']['score'] * self.evaluation_weights['structure_format']
        }
        
        return round(sum(scores.values()), 2)

    def _check_minimum_standards(self, scores: Dict) -> Dict:
        """Check if scores meet minimum standards"""
        results = {}
        for criterion, score in scores.items():
            min_score = self.minimum_scores.get(criterion, 70)
            results[criterion] = score >= min_score
        
        return {
            'meets_all_standards': all(results.values()),
            'criteria_results': results
        }

    def _identify_strengths(self, evaluation_results: Dict) -> List[str]:
        """Identify letter strengths"""
        strengths = []
        
        # Content strengths
        if evaluation_results['content']['score'] >= self.minimum_scores['content_relevance']:
            strengths.extend([
                f"Effectively addresses: {req}" 
                for req in evaluation_results['content']['addressed_requirements'][:3]
            ])
        
        # Tone strengths
        if evaluation_results['tone']['score'] >= self.minimum_scores['professional_tone']:
            strengths.extend(evaluation_results['tone']['strengths'])
        
        # Customization strengths
        if evaluation_results['custom']['score'] >= self.minimum_scores['customization']:
            strengths.extend([
                f"Company-specific content: {elem}"
                for elem in evaluation_results['custom']['company_specific'][:3]
            ])
        
        # Format strengths
        if evaluation_results['format']['score'] >= self.minimum_scores['structure_format']:
            strengths.extend(evaluation_results['format']['strengths'])
        
        return list(set(strengths))  # Remove duplicates

    def _identify_improvements(self, evaluation_results: Dict) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []
        
        # Content improvements
        if evaluation_results['content']['score'] < self.minimum_scores['content_relevance']:
            improvements.extend([
                f"Address requirement: {req}"
                for req in evaluation_results['content']['missing_requirements']
            ])
        
        # Tone improvements
        if evaluation_results['tone']['score'] < self.minimum_scores['professional_tone']:
            improvements.extend(evaluation_results['tone']['issues'])
        
        # Customization improvements
        if evaluation_results['custom']['score'] < self.minimum_scores['customization']:
            improvements.extend([
                f"Replace generic content: {elem}"
                for elem in evaluation_results['custom']['generic_elements']
            ])
        
        # Format improvements
        if evaluation_results['format']['score'] < self.minimum_scores['structure_format']:
            improvements.extend(evaluation_results['format']['issues'])
        
        return list(set(improvements))  # Remove duplicates