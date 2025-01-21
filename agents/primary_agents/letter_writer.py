from typing import Dict, List, Optional, Tuple
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json
import re

from models.model_manager import ModelManager
from agents.primary_agents.job_analyzer import JobAnalyzer
from agents.primary_agents.cv_matcher import CVMatcher

load_dotenv()

class LetterWriter:
    def __init__(self):
        self._setup_logger()
        self.model_manager = ModelManager()
        self.job_analyzer = JobAnalyzer()
        self.cv_matcher = CVMatcher()
        
        # Letter formats
        self.letter_formats = {
            'formal': {
                'salutation': True,
                'company_address': True,
                'formal_closing': True
            },
            'modern': {
                'salutation': True,
                'company_address': False,
                'formal_closing': False
            },
            'creative': {
                'salutation': True,
                'company_address': False,
                'formal_closing': True
            }
        }
        
        self.logger.info("Letter Writer initialized successfully")

    def _setup_logger(self):
        self.logger = logging.getLogger('LetterWriter')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/letter_writer_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def generate_cover_letter(
        self, 
        cv_text: str, 
        job_description: str, 
        company_name: str,
        format_style: str = 'formal'
    ) -> Dict:
        """Generate a customized cover letter"""
        self.logger.info("Starting cover letter generation")
        try:
            # Analyze job requirements and company tone
            job_analysis = self.job_analyzer.analyze_job(job_description)
            
            # Get CV-Job match analysis
            match_analysis = self.cv_matcher.match_cv_to_job(cv_text, job_description)
            
            # Generate letter content
            letter_content = self._generate_letter_content(
                cv_text,
                job_analysis,
                match_analysis,
                company_name
            )
            
            # Format the letter
            formatted_letter = self._format_letter(
                letter_content,
                company_name,
                format_style
            )
            
            # Generate tone and style analysis
            style_analysis = self._analyze_letter_style(formatted_letter)
            
            return {
                'letter': formatted_letter['final_letter'],
                'structure': {
                    'sections': formatted_letter['sections'],
                    'format_used': format_style,
                    'word_count': len(formatted_letter['final_letter'].split())
                },
                'style_analysis': style_analysis,
                'matching_achievements': letter_content['achievements'],
                'key_points_included': letter_content['key_points']
            }
            
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {str(e)}")
            raise

    def _generate_letter_content(self, cv_text: str, job_analysis: Dict, match_analysis: Dict, company_name: str) -> Dict:
        """Generate the main content of the cover letter"""
        try:
            generation_prompt = self._create_content_prompt(
                cv_text, job_analysis, match_analysis, company_name
            )
            
            response = self.model_manager.get_structured_completion(
                prompt=generation_prompt,
                output_schema={
                    "introduction": "string",
                    "body_paragraphs": ["list of paragraphs"],
                    "closing": "string",
                    "achievements": ["list of highlighted achievements"],
                    "key_points": ["list of key points addressed"]
                },
                task_type='letter_writing',
                system_message="You are an expert cover letter writer with deep understanding of professional communication."
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating letter content: {str(e)}")
            raise

    def _create_content_prompt(self, cv_text: str, job_analysis: Dict, match_analysis: Dict, company_name: str) -> str:
        """Create prompt for letter content generation"""
        return f"""
        Write a compelling cover letter for {company_name} based on the following:
        
        Job Requirements:
        - Required Skills: {', '.join(job_analysis['requirements']['required_skills'])}
        - Experience Level: {job_analysis['requirements'].get('experience', 'Not specified')}
        - Job Level: {job_analysis.get('job_details', {}).get('level', 'Not specified')}
        
        Matching Qualifications:
        - Matching Skills: {', '.join(match_analysis['skills_match']['matched_required'])}
        - Experience Match: {match_analysis['experience_match'].get('meets_requirement', 'Not specified')}
        
        Candidate Background:
        {cv_text}
        
        Company Culture Indicators:
        {', '.join(job_analysis.get('company_culture', {}).get('indicators', []))}
        
        Guidelines:
        1. Focus on matching qualifications
        2. Highlight relevant achievements
        3. Show enthusiasm for the company
        4. Address specific job requirements
        5. Maintain professional tone
        
        Structure the response with clear introduction, body paragraphs, and closing.
        """

    def _format_letter(self, content: Dict, company_name: str, format_style: str) -> Dict:
        """Format the cover letter according to chosen style"""
        format_config = self.letter_formats.get(format_style, self.letter_formats['formal'])
        
        sections = []
        final_letter = ""
        
        # Add date
        today = datetime.now().strftime("%B %d, %Y")
        final_letter += f"{today}\n\n"
        sections.append('date')
        
        # Add company address if required
        if format_config['company_address']:
            final_letter += f"{company_name}\n[Company Address]\n\n"
            sections.append('company_address')
        
        # Add salutation if required
        if format_config['salutation']:
            final_letter += "Dear Hiring Manager,\n\n"
            sections.append('salutation')
        
        # Add main content
        final_letter += content['introduction'] + "\n\n"
        sections.append('introduction')
        
        for paragraph in content['body_paragraphs']:
            final_letter += paragraph + "\n\n"
            sections.append('body_paragraph')
        
        final_letter += content['closing'] + "\n\n"
        sections.append('closing')
        
        # Add formal closing if required
        if format_config['formal_closing']:
            final_letter += "Sincerely,\n[Your Name]"
            sections.append('signature')
        
        return {
            'final_letter': final_letter,
            'sections': sections
        }

    def _analyze_letter_style(self, letter_data: Dict) -> Dict:
        """Analyze the style and tone of the generated letter"""
        letter_text = letter_data['final_letter']
        
        # Basic style analysis
        analysis = {
            'tone': self._determine_tone(letter_text),
            'structure_completeness': len(letter_data['sections']),
            'length_appropriate': 250 <= len(letter_text.split()) <= 400,
            'has_key_components': all(
                section in letter_data['sections']
                for section in ['introduction', 'body_paragraph', 'closing']
            )
        }
        
        return analysis

    def _determine_tone(self, text: str) -> str:
        """Determine the tone of the letter"""
        try:
            tone_analysis = self.model_manager.get_structured_completion(
                prompt=f"Analyze the tone of this text:\n\n{text}",
                output_schema={
                    "primary_tone": "string",
                    "formality_level": "string",
                    "enthusiasm_level": "string"
                },
                task_type='tone_analysis'
            )
            
            return tone_analysis['primary_tone']
            
        except Exception as e:
            self.logger.error(f"Error analyzing tone: {str(e)}")
            return "professional"  # Default fallback

    def validate_letter(self, letter_text: str, job_description: str) -> Dict:
        """Validate the generated cover letter"""
        try:
            validation_result = self.model_manager.get_structured_completion(
                prompt=f"""
                Validate this cover letter against the job description:
                
                Cover Letter:
                {letter_text}
                
                Job Description:
                {job_description}
                """,
                output_schema={
                    "is_relevant": "boolean",
                    "addresses_key_requirements": "boolean",
                    "professional_tone": "boolean",
                    "improvement_suggestions": ["list of suggestions"]
                },
                task_type='letter_validation'
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating letter: {str(e)}")
            raise