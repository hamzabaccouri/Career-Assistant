# agents/cv_analyzer.py

from typing import Dict, List, Optional
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from models.model_manager import ModelManager
from utils.text_analyzer import TextAnalyzer
from utils.ats_rules import ATSRules

load_dotenv()

class CVAnalyzer:
    def __init__(self):
        self._setup_logger()
        self.model_manager = ModelManager()
        self.text_analyzer = TextAnalyzer()
        self.ats_rules = ATSRules()
        
        # Define analysis components
        self.analysis_components = {
            'basic_analysis': True,   # Text-based analysis
            'ats_validation': True,   # ATS compliance check
            'detailed_skills': True,  # Technical skills analysis
            'experience_extraction': True  # Experience parsing
        }
        
        self.logger.info("CV Analyzer initialized successfully")

    def _setup_logger(self):
        """Configure logging"""
        self.logger = logging.getLogger('CVAnalyzer')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/cv_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def analyze_cv(self, cv_text: str) -> Dict:
        """
        Perform comprehensive CV analysis using multiple components
        """
        self.logger.info("Starting CV analysis")
        try:
            # Get initial LLM analysis
            llm_analysis = self.model_manager.analyze_cv(cv_text)
            
            # Perform text analysis
            text_analysis = self.text_analyzer.extract_keywords(cv_text)
            
            # Check ATS compliance
            ats_validation = self.validate_ats_compliance(cv_text)
            
            # Combine all analyses
            analysis = {
                'skills': {
                    'technical_skills': text_analysis.get('technical_terms', []),
                    'soft_skills': llm_analysis.get('skills', []),
                    'missing_critical_skills': ats_validation.get('missing_skills', [])
                },
                'experience': {
                    'years': llm_analysis.get('experience_years', 0),
                    'key_achievements': llm_analysis.get('key_achievements', []),
                    'highlighted_positions': text_analysis.get('nouns', [])
                },
                'ats_compliance': {
                    'is_compliant': ats_validation.get('is_compliant', False),
                    'issues': ats_validation.get('issues', []),
                    'format_score': ats_validation.get('format_score', 0)
                },
                'improvements': {
                    'suggestions': llm_analysis.get('improvement_suggestions', []),
                    'ats_recommendations': ats_validation.get('recommendations', []),
                    'content_recommendations': self._generate_content_recommendations(
                        text_analysis, llm_analysis, ats_validation
                    )
                }
            }
            
            self.logger.info("CV analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error during CV analysis: {str(e)}")
            raise

    def validate_ats_compliance(self, cv_text: str) -> Dict:
        """
        Check CV against ATS rules
        """
        try:
            # Extract sections from CV
            sections = self.text_analyzer.extract_sections(cv_text)
            
            # Validate structure
            structure_validation = self.ats_rules.validate_structure(
                list(sections.keys())
            )
            
            # Get file format validation (assuming PDF/DOCX)
            format_validation = self.ats_rules.validate_format(
                '.pdf',  # This should be dynamic based on actual file
                5  # Assumed file size in MB
            )
            
            # Combine validations
            compliance_result = {
                'is_compliant': structure_validation['valid'] and format_validation['valid'],
                'issues': structure_validation.get('issues', []) + format_validation.get('issues', []),
                'format_score': 100 if format_validation['valid'] else 50,
                'missing_skills': [],
                'recommendations': self.ats_rules.get_optimization_guidelines()
            }
            
            return compliance_result
            
        except Exception as e:
            self.logger.error(f"Error during ATS validation: {str(e)}")
            raise

    def _generate_content_recommendations(self, 
                                       text_analysis: Dict,
                                       llm_analysis: Dict,
                                       ats_validation: Dict) -> List[str]:
        """
        Generate content improvement recommendations based on all analyses
        """
        recommendations = []
        
        # Check keyword density
        if text_analysis.get('technical_terms', []):
            recommendations.append(
                "Consider adding more industry-specific keywords throughout your CV"
            )
        
        # Check achievements
        if not llm_analysis.get('key_achievements', []):
            recommendations.append(
                "Add specific, quantifiable achievements for each role"
            )
        
        # Check ATS compliance
        if not ats_validation.get('is_compliant', False):
            recommendations.append(
                "Update CV format to improve ATS compatibility"
            )
        
        return recommendations

    def get_cv_score(self, analysis: Dict) -> float:
        """
        Calculate overall CV score based on analysis results
        """
        try:
            scores = {
                'skills_score': self._calculate_skills_score(analysis['skills']),
                'experience_score': self._calculate_experience_score(analysis['experience']),
                'ats_score': analysis['ats_compliance']['format_score'],
                'content_score': self._calculate_content_score(analysis)
            }
            
            # Calculate weighted average
            weights = {
                'skills_score': 0.3,
                'experience_score': 0.3,
                'ats_score': 0.2,
                'content_score': 0.2
            }
            
            total_score = sum(
                score * weights[key] for key, score in scores.items()
            )
            
            return round(total_score, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating CV score: {str(e)}")
            return 0.0

    def _calculate_skills_score(self, skills_data: Dict) -> float:
        """Calculate score based on skills analysis"""
        technical_skills = len(skills_data.get('technical_skills', []))
        soft_skills = len(skills_data.get('soft_skills', []))
        missing_skills = len(skills_data.get('missing_critical_skills', []))
        
        # Basic scoring logic
        base_score = min((technical_skills + soft_skills) * 10, 100)
        penalty = missing_skills * 10
        
        return max(0, min(base_score - penalty, 100))

    def _calculate_experience_score(self, experience_data: Dict) -> float:
        """Calculate score based on experience analysis"""
        years = experience_data.get('years', 0)
        achievements = len(experience_data.get('key_achievements', []))
        
        # Basic scoring logic
        years_score = min(years * 10, 50)  # Cap at 50
        achievements_score = min(achievements * 10, 50)  # Cap at 50
        
        return years_score + achievements_score

    def _calculate_content_score(self, analysis: Dict) -> float:
        """Calculate score based on content quality"""
        improvements_needed = len(analysis['improvements']['suggestions'])
        content_score = 100 - (improvements_needed * 10)
        return max(0, content_score)