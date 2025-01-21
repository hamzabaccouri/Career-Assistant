# agents/primary_agents/ats_optimizer.py
from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json
import re

from models.model_manager import ModelManager
from utils.ats_rules import ATSRules
from agents.primary_agents.job_analyzer import JobAnalyzer
from agents.primary_agents.cv_matcher import CVMatcher

load_dotenv()

class ATSOptimizer:
    def __init__(self):
        self._setup_logger()
        self.model_manager = ModelManager()
        self.ats_rules = ATSRules()
        self.job_analyzer = JobAnalyzer()
        self.cv_matcher = CVMatcher()
        
        self.optimization_priorities = {
            'keyword_optimization': True,
            'format_optimization': True,
            'content_restructuring': True,
            'section_ordering': True
        }
        
        self.logger.info("ATS Optimizer initialized successfully")

    def _setup_logger(self):
        self.logger = logging.getLogger('ATSOptimizer')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/ats_optimizer_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def optimize_cv(self, cv_text: str, job_description: str) -> Dict:
        """Optimize CV for ATS based on job description"""
        self.logger.info("Starting CV optimization")
        try:
            # Initial matching
            initial_match = self.cv_matcher.match_cv_to_job(cv_text, job_description)
            
            # Get optimization suggestions from LLM
            optimized_content = self._get_llm_optimization(
                cv_text, 
                job_description, 
                initial_match['overall_match']['score']
            )
            
            # Final matching
            final_match = self.cv_matcher.match_cv_to_job(
                optimized_content['optimized_text'],
                job_description
            )
            
            # Calculate improvements
            improvements = self._calculate_improvements(
                optimized_content,
                initial_match['overall_match']['score'],
                final_match['overall_match']['score']
            )
            
            return {
                'optimized_cv': optimized_content['optimized_text'],
                'improvements': improvements,
                'optimization_details': {
                    'initial_score': initial_match['overall_match']['score'],
                    'final_score': final_match['overall_match']['score'],
                    'changes_made': optimized_content['changes'],
                    'format_suggestions': optimized_content['format_suggestions']
                },
                'recommendations': optimized_content['recommendations']
            }
            
        except Exception as e:
            self.logger.error(f"Error during CV optimization: {str(e)}")
            raise

    def _get_llm_optimization(self, cv_text: str, job_description: str, initial_score: float) -> Dict:
        """Get optimization suggestions from LLM"""
        prompt = f"""
        As an ATS optimization expert, improve this CV to better match the job description.
        Current match score: {initial_score}/100

        Job Description:
        {job_description}

        Current CV:
        {cv_text}

        Provide response in the following structure:
        1. Optimized CV text
        2. List of specific changes made
        3. Format suggestions
        4. Additional recommendations
        """

        try:
            response = self.model_manager.get_structured_completion(
                prompt=prompt,
                output_schema={
                    "optimized_text": "string",
                    "changes": ["list of changes made"],
                    "format_suggestions": ["list of format improvements"],
                    "recommendations": ["list of additional recommendations"]
                },
                task_type='cv_optimization',
                system_message="You are an expert ATS optimization system."
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting LLM optimization: {str(e)}")
            raise

    def _calculate_improvements(self, 
                              optimization_content: Dict,
                              initial_score: float,
                              final_score: float) -> Dict:
        """Calculate improvements made during optimization"""
        return {
            'score_improvement': round(final_score - initial_score, 2),
            'changes_made': len(optimization_content['changes']),
            'format_improvements': len(optimization_content['format_suggestions']),
            'has_significant_improvement': (final_score - initial_score) > 10
        }

    def validate_optimization(self, optimized_cv: str, job_description: str) -> Dict:
        """Validate optimization results"""
        try:
            # Get sections
            sections = [
                section.strip()
                for section in re.split(r'\n\s*\n', optimized_cv)
                if section.strip()
            ]
            
            # Check ATS compliance
            ats_check = self.ats_rules.validate_structure(sections)
            
            # Get final match
            final_match = self.cv_matcher.match_cv_to_job(
                optimized_cv,
                job_description
            )
            
            return {
                'is_ats_compliant': ats_check['valid'],
                'match_score': final_match['overall_match']['score'],
                'compliance_issues': ats_check.get('issues', []),
                'successful_optimization': final_match['overall_match']['score'] >= 75
            }
            
        except Exception as e:
            self.logger.error(f"Error validating optimization: {str(e)}")
            raise