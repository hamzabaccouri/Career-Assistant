from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from models.model_manager import ModelManager
from utils.text_analyzer import TextAnalyzer
from agents.primary_agents.cv_analyzer import CVAnalyzer
from agents.primary_agents.job_analyzer import JobAnalyzer

load_dotenv()

class CVMatcher:
    def __init__(self):
        self._setup_logger()
        self.model_manager = ModelManager()
        self.text_analyzer = TextAnalyzer()
        self.cv_analyzer = CVAnalyzer()
        self.job_analyzer = JobAnalyzer()
        
        self.matching_weights = {
            'required_skills': 0.4,
            'experience': 0.3,
            'education': 0.2,
            'soft_skills': 0.1
        }
        
        self.logger.info("CV Matcher initialized successfully")

    def _setup_logger(self):
        """Configure logging"""
        self.logger = logging.getLogger('CVMatcher')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/cv_matcher_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _extract_years(self, value: any) -> int:
        """Helper method to extract years from various input types"""
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                # Extract digits and convert to int
                digits = ''.join(filter(str.isdigit, value))
                return int(digits) if digits else 0
            return 0
        except Exception:
            return 0

    def match_cv_to_job(self, cv_text: str, job_description: str) -> Dict:
        """Match CV against job description with detailed analysis"""
        self.logger.info("Starting CV matching process")
        try:
            # Get CV and job analyses
            cv_analysis = self.cv_analyzer.analyze_cv(cv_text)
            job_analysis = self.job_analyzer.analyze_job(job_description)
            
            # Calculate matches for different components
            skills_match = self._calculate_skills_match(cv_analysis, job_analysis)
            experience_match = self._calculate_experience_match(cv_analysis, job_analysis)
            education_match = self._calculate_education_match(cv_analysis, job_analysis)
            
            # Calculate overall match score
            match_score = (
                skills_match['score'] * self.matching_weights['required_skills'] +
                experience_match['score'] * self.matching_weights['experience'] +
                education_match['score'] * self.matching_weights['education']
            )
            
            # Generate match analysis
            match_analysis = {
                'overall_match': {
                    'score': round(match_score, 2),
                    'confidence': self._calculate_confidence(cv_analysis, job_analysis),
                    'match_level': self._get_match_level(match_score)
                },
                'skills_match': skills_match,
                'experience_match': experience_match,
                'education_match': education_match,
                'recommendations': self._generate_recommendations(
                    cv_analysis, job_analysis, skills_match
                )
            }
            
            self.logger.info(f"Match analysis completed with score: {match_score}")
            return match_analysis
            
        except Exception as e:
            self.logger.error(f"Error during CV matching: {str(e)}")
            raise

    def _calculate_skills_match(self, cv_analysis: Dict, job_analysis: Dict) -> Dict:
        """Calculate skills match score and details"""
        try:
            required_skills = set(job_analysis.get('requirements', {}).get('required_skills', []))
            preferred_skills = set(job_analysis.get('requirements', {}).get('preferred_skills', []))
            cv_skills = set(cv_analysis.get('skills', {}).get('technical_skills', []))
            
            # Calculate matches
            required_matches = cv_skills.intersection(required_skills)
            preferred_matches = cv_skills.intersection(preferred_skills)
            
            # Calculate score
            if len(required_skills) == 0:
                required_score = 100
            else:
                required_score = (len(required_matches) / len(required_skills)) * 100
            
            if len(preferred_skills) == 0:
                preferred_score = 100
            else:
                preferred_score = (len(preferred_matches) / len(preferred_skills)) * 100
            
            # Weight required skills more heavily
            total_score = (required_score * 0.7) + (preferred_score * 0.3)
            
            return {
                'score': round(total_score, 2),
                'matched_required': list(required_matches),
                'matched_preferred': list(preferred_matches),
                'missing_required': list(required_skills - cv_skills),
                'missing_preferred': list(preferred_skills - cv_skills)
            }
        except Exception as e:
            self.logger.error(f"Error calculating skills match: {str(e)}")
            return {
                'score': 0,
                'matched_required': [],
                'matched_preferred': [],
                'missing_required': [],
                'missing_preferred': []
            }

    def _calculate_experience_match(self, cv_analysis: Dict, job_analysis: Dict) -> Dict:
        """Calculate experience match score and details"""
        try:
            cv_years = self._extract_years(cv_analysis.get('experience', {}).get('years', 0))
            required_years = self._extract_years(job_analysis.get('requirements', {}).get('experience', 0))
            
            # Calculate score
            if required_years == 0:
                score = 100
            elif cv_years >= required_years:
                score = 100
            else:
                score = (cv_years / required_years) * 100 if required_years > 0 else 0
            
            return {
                'score': round(score, 2),
                'cv_years': cv_years,
                'required_years': required_years,
                'meets_requirement': cv_years >= required_years
            }
        except Exception as e:
            self.logger.error(f"Error calculating experience match: {str(e)}")
            return {
                'score': 0,
                'cv_years': 0,
                'required_years': 0,
                'meets_requirement': False
            }

    def _calculate_education_match(self, cv_analysis: Dict, job_analysis: Dict) -> Dict:
        """Calculate education match score"""
        try:
            education_levels = {
                'phd': 4,
                'doctorate': 4,
                'master': 3,
                'bachelor': 2,
                'associate': 1,
                'high school': 0
            }
            
            # Get education requirements
            required_edu = str(job_analysis.get('requirements', {}).get('education', '')).lower()
            cv_edu = str(cv_analysis.get('education', '')).lower()
            
            # Determine levels
            required_level = 0
            cv_level = 0
            
            # Find highest matching level for each
            for level, score in education_levels.items():
                if level in required_edu:
                    required_level = max(required_level, score)
                if level in cv_edu:
                    cv_level = max(cv_level, score)
            
            # Calculate score
            if required_level == 0:
                score = 100  # No specific requirement
            elif cv_level >= required_level:
                score = 100  # Meets or exceeds requirement
            else:
                score = (cv_level / required_level) * 100 if required_level > 0 else 0
            
            return {
                'score': round(score, 2),
                'cv_level': cv_level,
                'required_level': required_level,
                'meets_requirement': cv_level >= required_level,
                'cv_education': cv_edu,
                'required_education': required_edu
            }
        except Exception as e:
            self.logger.error(f"Error calculating education match: {str(e)}")
            return {
                'score': 0,
                'cv_level': 0,
                'required_level': 0,
                'meets_requirement': False,
                'cv_education': '',
                'required_education': ''
            }

    def _calculate_confidence(self, cv_analysis: Dict, job_analysis: Dict) -> float:
        """Calculate confidence in the match analysis"""
        try:
            # Extract and convert experience years to int
            exp_years = self._extract_years(cv_analysis.get('experience', {}).get('years', 0))
            
            # Calculate confidence factors
            factors = [
                float(cv_analysis.get('ats_compliance', {}).get('format_score', 0)) / 100,
                bool(cv_analysis.get('skills', {}).get('technical_skills', [])),
                bool(job_analysis.get('requirements', {}).get('required_skills', [])),
                exp_years > 0
            ]
            
            confidence = sum(1 for factor in factors if factor) / len(factors)
            return round(confidence * 100, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0

    def _get_match_level(self, score: float) -> str:
        """Determine match level based on score"""
        if score >= 90:
            return "Excellent Match"
        elif score >= 75:
            return "Strong Match"
        elif score >= 60:
            return "Good Match"
        elif score >= 40:
            return "Partial Match"
        else:
            return "Low Match"

    def _generate_recommendations(self, cv_analysis: Dict, job_analysis: Dict, skills_match: Dict) -> List[str]:
        """Generate recommendations for improving match"""
        try:
            recommendations = []
            
            # Skills recommendations
            if skills_match.get('missing_required', []):
                recommendations.append(
                    f"Add experience with: {', '.join(skills_match['missing_required'])}"
                )
            
            if skills_match.get('missing_preferred', []):
                recommendations.append(
                    f"Consider adding experience with: {', '.join(skills_match['missing_preferred'])}"
                )
            
            # Experience check
            cv_years = self._extract_years(cv_analysis.get('experience', {}).get('years', 0))
            req_years = self._extract_years(job_analysis.get('requirements', {}).get('experience_years', 0))
            
            if cv_years < req_years:
                recommendations.append("Highlight more relevant work experience")
            
            # Format recommendations
            if float(cv_analysis.get('ats_compliance', {}).get('format_score', 0)) < 80:
                recommendations.append("Improve CV format for better ATS compatibility")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []