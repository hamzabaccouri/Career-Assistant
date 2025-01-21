# models/model_manager.py
from typing import Dict, List, Optional, Any
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from models.openai_handler import OpenAIHandler 
from models.anthropic_handler import AnthropicHandler

load_dotenv()

class ModelManager:
   def __init__(self):
       self._setup_logger()
       self.openai_handler = OpenAIHandler()
       self.anthropic_handler = AnthropicHandler()
       
       self.model_config = {
           'default': 'openai',
           'fallback_order': ['openai', 'anthropic'],
           'task_preferences': {
               'cv_analysis': 'anthropic',
               'job_matching': 'openai',
               'ats_optimization': 'anthropic'
           }
       }
       
       self.logger.info("Model Manager initialized successfully")

   def _setup_logger(self):
       self.logger = logging.getLogger('ModelManager')
       self.logger.setLevel(logging.INFO)
       
       os.makedirs('logs', exist_ok=True)
       formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
       
       file_handler = logging.FileHandler(
           f'logs/model_manager_{datetime.now().strftime("%Y%m%d")}.log'
       )
       file_handler.setFormatter(formatter)
       self.logger.addHandler(file_handler)

   def get_completion(self, 
                     prompt: str, 
                     task_type: Optional[str] = None,
                     preferred_service: Optional[str] = None) -> str:
       service = preferred_service or self.model_config['task_preferences'].get(
           task_type, self.model_config['default']
       )
       
       self.logger.info(f"Attempting completion with service: {service}")
       
       try:
           if service == 'openai':
               return self.openai_handler.get_completion(prompt)
           elif service == 'anthropic':
               return self.anthropic_handler.get_completion(prompt)
           
       except Exception as e:
           self.logger.error(f"Error with {service}: {str(e)}")
           for fallback_service in self.model_config['fallback_order']:
               if fallback_service != service:
                   self.logger.info(f"Attempting fallback to {fallback_service}")
                   try:
                       if fallback_service == 'openai':
                           return self.openai_handler.get_completion(prompt)
                       elif fallback_service == 'anthropic':
                           return self.anthropic_handler.get_completion(prompt)
                   except Exception as fallback_error:
                       self.logger.error(f"Fallback to {fallback_service} failed: {str(fallback_error)}")
           
           raise Exception("All services failed")

   def get_structured_completion(self, 
                               prompt: str,
                               output_schema: Dict,
                               task_type: Optional[str] = None,
                               system_message: Optional[str] = None) -> Dict:
       service = self.model_config['task_preferences'].get(
           task_type, self.model_config['default']
       )
       
       self.logger.info(f"Attempting structured completion with service: {service}")
       
       try:
           if service == 'openai':
               return self.openai_handler.get_structured_completion(
                   prompt, output_schema, system_message
               )
           elif service == 'anthropic':
               return self.anthropic_handler.get_structured_completion(
                   prompt, output_schema, system_message
               )
           
       except Exception as e:
           self.logger.error(f"Error with {service}: {str(e)}")
           for fallback_service in self.model_config['fallback_order']:
               if fallback_service != service:
                   self.logger.info(f"Attempting fallback to {fallback_service}")
                   try:
                       if fallback_service == 'openai':
                           return self.openai_handler.get_structured_completion(
                               prompt, output_schema, system_message
                           )
                       elif fallback_service == 'anthropic':
                           return self.anthropic_handler.get_structured_completion(
                               prompt, output_schema, system_message
                           )
                   except Exception as fallback_error:
                       self.logger.error(f"Fallback to {fallback_service} failed: {str(fallback_error)}")
           
           raise Exception("All services failed")

   def analyze_cv(self, cv_text: str) -> Dict:
       return self.get_structured_completion(
           prompt=cv_text,
           output_schema={
               "skills": ["list of skills"],
               "experience_years": "number",
               "key_achievements": ["list of achievements"],
               "missing_elements": ["list of missing important elements"],
               "improvement_suggestions": ["list of suggestions"]
           },
           task_type='cv_analysis',
           system_message="You are an expert CV analyzer."
       )

   def match_job(self, cv_text: str, job_description: str) -> Dict:
       return self.get_structured_completion(
           prompt=f"CV:\n{cv_text}\n\nJob Description:\n{job_description}",
           output_schema={
               "match_percentage": "number between 0 and 100",
               "matching_skills": ["list of matching skills"],
               "missing_skills": ["list of required skills not found in CV"],
               "recommendations": ["list of recommendations to improve match"]
           },
           task_type='job_matching',
           system_message="You are an expert ATS system."
       )