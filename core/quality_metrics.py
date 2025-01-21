from typing import Dict, List, Union, Optional
import logging
import os
from datetime import datetime

class QualityMetrics:
    def __init__(self):
        self._setup_logger()
        
        # Define scoring weights
        self.score_weights = {
            'cv': {
                'content_relevance': 0.3,
                'skills_match': 0.25,
                'experience_quality': 0.25,
                'format_compliance': 0.2
            },
            'letter': {
                'customization': 0.3,
                'content_relevance': 0.3,
                'professional_tone': 0.2,
                'formatting': 0.2
            },
            'ats': {
                'keyword_optimization': 0.3,
                'format_compliance': 0.3,
                'section_structure': 0.2,
                'content_clarity': 0.2
            }
        }
        
        # Define minimum thresholds
        self.quality_thresholds = {
            'cv_minimum_score': 75,
            'letter_minimum_score': 75,
            'ats_minimum_score': 75,
            'overall_minimum_score': 75
        }
        
        self.logger.info("Quality Metrics initialized")

    def _setup_logger(self):
        """Configure logging"""
        self.logger = logging.getLogger('QualityMetrics')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/quality_metrics_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def calculate_cv_score(self, metrics: Dict) -> Dict:
        """Calculate CV quality score"""
        try:
            scores = {
                'content_score': (
                    metrics.get('content_relevance', 0) * 
                    self.score_weights['cv']['content_relevance']
                ),
                'skills_score': (
                    metrics.get('skills_match', 0) * 
                    self.score_weights['cv']['skills_match']
                ),
                'experience_score': (
                    metrics.get('experience_quality', 0) * 
                    self.score_weights['cv']['experience_quality']
                ),
                'format_score': (
                    metrics.get('format_compliance', 0) * 
                    self.score_weights['cv']['format_compliance']
                )
            }
            
            total_score = sum(scores.values())
            meets_threshold = total_score >= self.quality_thresholds['cv_minimum_score']
            
            return {
                'total_score': round(total_score, 2),
                'component_scores': scores,
                'meets_threshold': meets_threshold
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating CV score: {str(e)}")
            raise

    def calculate_letter_score(self, metrics: Dict) -> Dict:
        """Calculate cover letter quality score"""
        try:
            scores = {
                'customization_score': (
                    metrics.get('customization', 0) * 
                    self.score_weights['letter']['customization']
                ),
                'content_score': (
                    metrics.get('content_relevance', 0) * 
                    self.score_weights['letter']['content_relevance']
                ),
                'tone_score': (
                    metrics.get('professional_tone', 0) * 
                    self.score_weights['letter']['professional_tone']
                ),
                'format_score': (
                    metrics.get('formatting', 0) * 
                    self.score_weights['letter']['formatting']
                )
            }
            
            total_score = sum(scores.values())
            meets_threshold = total_score >= self.quality_thresholds['letter_minimum_score']
            
            return {
                'total_score': round(total_score, 2),
                'component_scores': scores,
                'meets_threshold': meets_threshold
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating letter score: {str(e)}")
            raise

    def calculate_ats_score(self, metrics: Dict) -> Dict:
        """Calculate ATS compliance score"""
        try:
            scores = {
                'keyword_score': (
                    metrics.get('keyword_optimization', 0) * 
                    self.score_weights['ats']['keyword_optimization']
                ),
                'format_score': (
                    metrics.get('format_compliance', 0) * 
                    self.score_weights['ats']['format_compliance']
                ),
                'structure_score': (
                    metrics.get('section_structure', 0) * 
                    self.score_weights['ats']['section_structure']
                ),
                'clarity_score': (
                    metrics.get('content_clarity', 0) * 
                    self.score_weights['ats']['content_clarity']
                )
            }
            
            total_score = sum(scores.values())
            meets_threshold = total_score >= self.quality_thresholds['ats_minimum_score']
            
            return {
                'total_score': round(total_score, 2),
                'component_scores': scores,
                'meets_threshold': meets_threshold
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating ATS score: {str(e)}")
            raise

    def calculate_overall_quality(self, cv_score: float, letter_score: float, ats_score: float) -> Dict:
        """Calculate overall application quality score"""
        try:
            # Weight distribution for overall score
            weights = {
                'cv': 0.4,
                'letter': 0.3,
                'ats': 0.3
            }
            
            overall_score = (
                cv_score * weights['cv'] +
                letter_score * weights['letter'] +
                ats_score * weights['ats']
            )
            
            meets_threshold = overall_score >= self.quality_thresholds['overall_minimum_score']
            
            return {
                'overall_score': round(overall_score, 2),
                'component_weights': weights,
                'meets_threshold': meets_threshold,
                'component_scores': {
                    'cv_score': cv_score,
                    'letter_score': letter_score,
                    'ats_score': ats_score
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating overall quality: {str(e)}")
            raise

    def get_quality_assessment(self, cv_metrics: Dict, letter_metrics: Dict, ats_metrics: Dict) -> Dict:
        """Get comprehensive quality assessment"""
        try:
            # Calculate individual scores
            cv_score = self.calculate_cv_score(cv_metrics)
            letter_score = self.calculate_letter_score(letter_metrics)
            ats_score = self.calculate_ats_score(ats_metrics)
            
            # Calculate overall quality
            overall_quality = self.calculate_overall_quality(
                cv_score['total_score'],
                letter_score['total_score'],
                ats_score['total_score']
            )
            
            return {
                'overall_quality': overall_quality,
                'cv_assessment': cv_score,
                'letter_assessment': letter_score,
                'ats_assessment': ats_score,
                'meets_all_thresholds': all([
                    cv_score['meets_threshold'],
                    letter_score['meets_threshold'],
                    ats_score['meets_threshold'],
                    overall_quality['meets_threshold']
                ])
            }
            
        except Exception as e:
            self.logger.error(f"Error in quality assessment: {str(e)}")
            raise

    def get_improvement_priorities(self, quality_assessment: Dict) -> List[str]:
        """Determine improvement priorities based on scores"""
        priorities = []
        
        # Check CV score
        if not quality_assessment['cv_assessment']['meets_threshold']:
            cv_scores = quality_assessment['cv_assessment']['component_scores']
            lowest_cv = min(cv_scores.items(), key=lambda x: x[1])[0]
            priorities.append(f"Improve CV {lowest_cv.replace('_score', '')}")
        
        # Check letter score
        if not quality_assessment['letter_assessment']['meets_threshold']:
            letter_scores = quality_assessment['letter_assessment']['component_scores']
            lowest_letter = min(letter_scores.items(), key=lambda x: x[1])[0]
            priorities.append(f"Improve letter {lowest_letter.replace('_score', '')}")
        
        # Check ATS score
        if not quality_assessment['ats_assessment']['meets_threshold']:
            ats_scores = quality_assessment['ats_assessment']['component_scores']
            lowest_ats = min(ats_scores.items(), key=lambda x: x[1])[0]
            priorities.append(f"Improve ATS {lowest_ats.replace('_score', '')}")
        
        return priorities