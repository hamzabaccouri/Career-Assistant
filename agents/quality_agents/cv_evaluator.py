from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from models.model_manager import ModelManager
from utils.text_analyzer import TextAnalyzer
from agents.primary_agents.cv_analyzer import CVAnalyzer

load_dotenv()

class CVEvaluator:
    def __init__(self):
        self._setup_logger()
        self.model_manager = ModelManager()
        self.text_analyzer = TextAnalyzer()
        self.cv_analyzer = CVAnalyzer()
        
        # Evaluation criteria weights
        self.evaluation_weights = {
            'content_quality': 0.3,
            'achievements': 0.25,
            'experience_presentation': 0.25,
            'skills_presentation': 0.2
        }
        
        self.logger.info("CV Evaluator initialized successfully")

    def _setup_logger(self):
        self.logger = logging.getLogger('CVEvaluator')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/cv_evaluator_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def evaluate_cv(self, cv_text: str, industry: Optional[str] = None) -> Dict:
        """
        Perform comprehensive CV evaluation
        """
        self.logger.info("Starting CV evaluation")
        try:
            # Get initial CV analysis
            cv_analysis = self.cv_analyzer.analyze_cv(cv_text)
            
            # Content quality evaluation
            content_eval = self._evaluate_content_quality(cv_text, cv_analysis)
            
            # Achievements evaluation
            achievements_eval = self._evaluate_achievements(cv_text, cv_analysis)
            
            # Experience presentation evaluation
            experience_eval = self._evaluate_experience(cv_text, cv_analysis)
            
            # Skills presentation evaluation
            skills_eval = self._evaluate_skills(cv_text, cv_analysis, industry)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score({
                'content': content_eval,
                'achievements': achievements_eval,
                'experience': experience_eval,
                'skills': skills_eval
            })
            
            evaluation_result = {
                'overall_score': overall_score,
                'evaluation_summary': {
                    'content_quality': content_eval,
                    'achievements_impact': achievements_eval,
                    'experience_presentation': experience_eval,
                    'skills_relevance': skills_eval
                },
                'strengths': self._identify_strengths({
                    'content': content_eval,
                    'achievements': achievements_eval,
                    'experience': experience_eval,
                    'skills': skills_eval
                }),
                'improvement_areas': self._identify_improvements({
                    'content': content_eval,
                    'achievements': achievements_eval,
                    'experience': experience_eval,
                    'skills': skills_eval
                }),
                'industry_alignment': self._evaluate_industry_alignment(cv_text, industry) if industry else None
            }
            
            self.logger.info(f"Evaluation completed with score: {overall_score}")
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"Error during CV evaluation: {str(e)}")
            raise

    def _evaluate_content_quality(self, cv_text: str, cv_analysis: Dict) -> Dict:
        """Evaluate CV content quality"""
        try:
            content_analysis = self.model_manager.get_structured_completion(
                prompt=f"Evaluate the content quality of this CV:\n\n{cv_text}",
                output_schema={
                    "clarity_score": "number between 0 and 100",
                    "conciseness_score": "number between 0 and 100",
                    "professionalism_score": "number between 0 and 100",
                    "content_issues": ["list of issues"],
                    "strong_points": ["list of strong points"]
                },
                task_type='cv_evaluation'
            )
            
            average_score = (
                content_analysis['clarity_score'] +
                content_analysis['conciseness_score'] +
                content_analysis['professionalism_score']
            ) / 3
            
            return {
                'score': average_score,
                'issues': content_analysis['content_issues'],
                'strengths': content_analysis['strong_points']
            }
            
        except Exception as e:
            self.logger.error(f"Error in content evaluation: {str(e)}")
            return {'score': 0, 'issues': ['Evaluation failed'], 'strengths': []}

    def _evaluate_achievements(self, cv_text: str, cv_analysis: Dict) -> Dict:
        """Evaluate achievements presentation"""
        try:
            achievements_analysis = self.model_manager.get_structured_completion(
                prompt=f"Evaluate the achievements in this CV:\n\n{cv_text}",
                output_schema={
                    "quantification_score": "number between 0 and 100",
                    "impact_score": "number between 0 and 100",
                    "relevance_score": "number between 0 and 100",
                    "weak_achievements": ["list of weak achievements"],
                    "strong_achievements": ["list of strong achievements"]
                },
                task_type='achievements_evaluation'
            )
            
            average_score = (
                achievements_analysis['quantification_score'] +
                achievements_analysis['impact_score'] +
                achievements_analysis['relevance_score']
            ) / 3
            
            return {
                'score': average_score,
                'weak_points': achievements_analysis['weak_achievements'],
                'strong_points': achievements_analysis['strong_achievements']
            }
            
        except Exception as e:
            self.logger.error(f"Error in achievements evaluation: {str(e)}")
            return {'score': 0, 'weak_points': [], 'strong_points': []}

    def _evaluate_experience(self, cv_text: str, cv_analysis: Dict) -> Dict:
        """Evaluate experience presentation"""
        try:
            experience_analysis = self.model_manager.get_structured_completion(
                prompt=f"Evaluate the experience presentation in this CV:\n\n{cv_text}",
                output_schema={
                    "progression_clarity": "number between 0 and 100",
                    "role_description_quality": "number between 0 and 100",
                    "responsibility_clarity": "number between 0 and 100",
                    "improvement_areas": ["list of areas to improve"],
                    "effective_points": ["list of effective points"]
                },
                task_type='experience_evaluation'
            )
            
            average_score = (
                experience_analysis['progression_clarity'] +
                experience_analysis['role_description_quality'] +
                experience_analysis['responsibility_clarity']
            ) / 3
            
            return {
                'score': average_score,
                'improvements': experience_analysis['improvement_areas'],
                'effective_aspects': experience_analysis['effective_points']
            }
            
        except Exception as e:
            self.logger.error(f"Error in experience evaluation: {str(e)}")
            return {'score': 0, 'improvements': [], 'effective_aspects': []}

    def _evaluate_skills(self, cv_text: str, cv_analysis: Dict, industry: Optional[str]) -> Dict:
        """Evaluate skills presentation"""
        try:
            skills_prompt = f"""
            Evaluate the skills presentation in this CV:
            
            CV Content:
            {cv_text}
            
            Industry Context:
            {industry if industry else 'Not specified'}
            """
            
            skills_analysis = self.model_manager.get_structured_completion(
                prompt=skills_prompt,
                output_schema={
                    "organization_score": "number between 0 and 100",
                    "relevance_score": "number between 0 and 100",
                    "specificity_score": "number between 0 and 100",
                    "missing_key_skills": ["list of missing skills"],
                    "well_presented_skills": ["list of well-presented skills"]
                },
                task_type='skills_evaluation'
            )
            
            average_score = (
                skills_analysis['organization_score'] +
                skills_analysis['relevance_score'] +
                skills_analysis['specificity_score']
            ) / 3
            
            return {
                'score': average_score,
                'missing_skills': skills_analysis['missing_key_skills'],
                'strong_skills': skills_analysis['well_presented_skills']
            }
            
        except Exception as e:
            self.logger.error(f"Error in skills evaluation: {str(e)}")
            return {'score': 0, 'missing_skills': [], 'strong_skills': []}

    def _calculate_overall_score(self, evaluation_results: Dict) -> float:
        """Calculate weighted overall score"""
        scores = {
            'content': evaluation_results['content']['score'] * self.evaluation_weights['content_quality'],
            'achievements': evaluation_results['achievements']['score'] * self.evaluation_weights['achievements'],
            'experience': evaluation_results['experience']['score'] * self.evaluation_weights['experience_presentation'],
            'skills': evaluation_results['skills']['score'] * self.evaluation_weights['skills_presentation']
        }
        
        return round(sum(scores.values()), 2)

    def _identify_strengths(self, evaluation_results: Dict) -> List[str]:
        """Identify CV strengths"""
        strengths = []
        
        # Content strengths
        if evaluation_results['content']['score'] >= 80:
            strengths.extend(evaluation_results['content']['strengths'])
        
        # Achievement strengths
        if evaluation_results['achievements']['score'] >= 80:
            strengths.extend(evaluation_results['achievements']['strong_points'])
        
        # Experience strengths
        if evaluation_results['experience']['score'] >= 80:
            strengths.extend(evaluation_results['experience']['effective_aspects'])
        
        # Skills strengths
        if evaluation_results['skills']['score'] >= 80:
            strengths.extend([f"Strong presentation of {skill}" for skill in evaluation_results['skills']['strong_skills']])
        
        return list(set(strengths))  # Remove duplicates

    def _identify_improvements(self, evaluation_results: Dict) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        # Content improvements
        if evaluation_results['content']['score'] < 80:
            improvements.extend(evaluation_results['content']['issues'])
        
        # Achievement improvements
        if evaluation_results['achievements']['score'] < 80:
            improvements.extend([f"Strengthen achievement: {a}" for a in evaluation_results['achievements']['weak_points']])
        
        # Experience improvements
        if evaluation_results['experience']['score'] < 80:
            improvements.extend(evaluation_results['experience']['improvements'])
        
        # Skills improvements
        if evaluation_results['skills']['score'] < 80:
            improvements.extend([f"Add missing skill: {skill}" for skill in evaluation_results['skills']['missing_skills']])
        
        return list(set(improvements))  # Remove duplicates

    def _evaluate_industry_alignment(self, cv_text: str, industry: str) -> Dict:
        """Evaluate CV alignment with industry standards"""
        try:
            alignment_analysis = self.model_manager.get_structured_completion(
                prompt=f"""
                Evaluate this CV's alignment with {industry} industry standards:
                
                CV Content:
                {cv_text}
                """,
                output_schema={
                    "alignment_score": "number between 0 and 100",
                    "industry_specific_strengths": ["list of strengths"],
                    "industry_gaps": ["list of gaps"],
                    "industry_recommendations": ["list of recommendations"]
                },
                task_type='industry_alignment'
            )
            
            return {
                'alignment_score': alignment_analysis['alignment_score'],
                'industry_strengths': alignment_analysis['industry_specific_strengths'],
                'industry_gaps': alignment_analysis['industry_gaps'],
                'recommendations': alignment_analysis['industry_recommendations']
            }
            
        except Exception as e:
            self.logger.error(f"Error in industry alignment evaluation: {str(e)}")
            return {
                'alignment_score': 0,
                'industry_strengths': [],
                'industry_gaps': [],
                'recommendations': ['Unable to evaluate industry alignment']
            }