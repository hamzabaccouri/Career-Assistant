# job_analyzer.py

from typing import Dict, List, Optional
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from models.model_manager import ModelManager
from utils.text_analyzer import TextAnalyzer

load_dotenv()

class JobAnalyzer:
    def __init__(self):
        self._setup_logger()
        self.model_manager = ModelManager()
        self.text_analyzer = TextAnalyzer()
        
        self.analysis_components = {
            'requirements': True,      # Required skills/qualifications
            'responsibilities': True,  # Job duties
            'company_culture': True,   # Company culture indicators
            'benefits': True          # Job benefits/perks
        }
        
        self.logger.info("Job Analyzer initialized successfully")

    def _setup_logger(self):
        """Configure logging"""
        self.logger = logging.getLogger('JobAnalyzer')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/job_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def analyze_job(self, job_description: str) -> Dict:
        """Perform comprehensive job description analysis using LLM"""
        self.logger.info("Starting job description analysis")
        try:
            # First pass: Basic text analysis for technical terms
            basic_analysis = self.text_analyzer.extract_keywords(job_description)
            
            # Second pass: Detailed LLM analysis
            prompt = f"""
            Analyze this job description and extract key information in a structured format:

            {job_description}

            Focus on:
            1. Required and preferred skills
            2. Experience and education requirements
            3. Key responsibilities
            4. Company culture indicators
            5. Benefits and perks
            6. Seniority level
            7. Technical requirements
            8. Soft skills required
            """
            
            llm_analysis = self.model_manager.get_structured_completion(
                prompt=prompt,
                output_schema={
                    "required_skills": ["list of required technical and professional skills"],
                    "preferred_skills": ["list of preferred additional skills"],
                    "experience_level": "detailed experience requirements",
                    "education_requirements": "education requirements",
                    "key_responsibilities": ["list of main job duties"],
                    "culture_indicators": ["list of company culture aspects"],
                    "benefits_and_perks": ["list of offered benefits"],
                    "seniority_level": "job level (e.g., Entry, Mid, Senior)",
                    "soft_skills": ["list of required soft skills"]
                },
                task_type="job_analysis"
            )
            
            # Combine analyses
            combined_analysis = {
                'requirements': {
                    'required_skills': llm_analysis.get('required_skills', []),
                    'preferred_skills': llm_analysis.get('preferred_skills', []),
                    'technical_skills': basic_analysis.get('technical_terms', []),
                    'soft_skills': llm_analysis.get('soft_skills', []),
                    'experience': llm_analysis.get('experience_level', ''),
                    'education': llm_analysis.get('education_requirements', '')
                },
                'job_details': {
                    'responsibilities': llm_analysis.get('key_responsibilities', []),
                    'seniority_level': llm_analysis.get('seniority_level', 'Not specified'),
                    'key_terms': basic_analysis.get('action_verbs', [])
                },
                'company_culture': {
                    'indicators': llm_analysis.get('culture_indicators', []),
                    'benefits': llm_analysis.get('benefits_and_perks', [])
                }
            }
            
            # Add complexity score
            combined_analysis['complexity_score'] = self._calculate_complexity_score(combined_analysis)
            
            self.logger.info("Job analysis completed successfully")
            return combined_analysis
            
        except Exception as e:
            self.logger.error(f"Error during job analysis: {str(e)}")
            raise

    def _calculate_complexity_score(self, analysis: Dict) -> int:
        """Calculate job complexity score based on requirements"""
        score = 0
        
        # Technical skills weight
        tech_skills = len(analysis['requirements']['technical_skills'])
        score += min(tech_skills * 10, 40)  # Max 40 points
        
        # Experience level weight
        experience = analysis['requirements']['experience'].lower()
        if 'senior' in experience or 'lead' in experience:
            score += 30
        elif 'mid' in experience or '3' in experience:
            score += 20
        else:
            score += 10
        
        # Education requirement weight
        education = analysis['requirements']['education'].lower()
        if 'phd' in education or 'doctorate' in education:
            score += 30
        elif 'master' in education or 'msc' in education:
            score += 20
        elif 'bachelor' in education or 'bsc' in education:
            score += 10
        
        return min(score, 100)  # Cap at 100

    def get_required_keywords(self, job_description: str) -> List[str]:
        """Extract essential keywords from job description"""
        try:
            # Get complete analysis
            analysis = self.analyze_job(job_description)
            
            # Combine all important keywords
            keywords = set()
            
            # Add all required skills
            keywords.update(analysis['requirements']['required_skills'])
            keywords.update(analysis['requirements']['technical_skills'])
            
            # Add key responsibility terms
            for resp in analysis['job_details']['responsibilities']:
                # Split and add significant words (length > 3)
                words = [w.lower() for w in resp.split() if len(w) > 3]
                keywords.update(words)
            
            # Convert to sorted list and return
            return sorted(list(keywords))
            
        except Exception as e:
            self.logger.error(f"Error extracting required keywords: {str(e)}")
            return []