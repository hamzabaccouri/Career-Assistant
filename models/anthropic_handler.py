# models/anthropic_handler.py

from typing import Dict, List, Optional, Any
import anthropic
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AnthropicHandler:
   def __init__(self, model: str = "claude-3-opus-20240229"):
       self._setup_logger()
       self.client = anthropic.Client(
           api_key=os.getenv('ANTHROPIC_API_KEY')
       )
       self.model = model
       
       self.model_configs = {
           'claude-3-opus-20240229': {
               'max_tokens': 4096,
               'temperature': 0.7,
           },
           'claude-3-sonnet-20240229': {
               'max_tokens': 4096,
               'temperature': 0.7,
           }
       }
       
       self.logger.info(f"Initialized Anthropic handler with model: {model}")

   def _setup_logger(self):
       self.logger = logging.getLogger('AnthropicHandler')
       self.logger.setLevel(logging.INFO)
       
       os.makedirs('logs', exist_ok=True)
       formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
       
       file_handler = logging.FileHandler(
           f'logs/anthropic_handler_{datetime.now().strftime("%Y%m%d")}.log'
       )
       file_handler.setFormatter(formatter)
       self.logger.addHandler(file_handler)

   def get_completion(self, 
                     prompt: str, 
                     system_message: Optional[str] = None,
                     temperature: Optional[float] = None,
                     max_tokens: Optional[int] = None) -> str:
       try:
           params = {
               "model": self.model,
               "max_tokens": max_tokens or self.model_configs[self.model]['max_tokens'],
               "temperature": temperature or self.model_configs[self.model]['temperature'],
               "messages": [{"role": "user", "content": prompt}]
           }
           
           if system_message:
               params["system"] = system_message
               
           message = self.client.messages.create(**params)
           return message.content[0].text

       except Exception as e:
           self.logger.error(f"Error getting completion: {str(e)}")
           raise

   def get_structured_completion(self, 
                               prompt: str,
                               output_schema: Dict,
                               system_message: Optional[str] = None) -> Dict:
       try:
           schema_prompt = (
               f"{prompt}\n\n"
               f"Please provide the response in the following JSON format: {json.dumps(output_schema, indent=2)}\n"
               f"Ensure the response is valid JSON."
           )
           
           response = self.get_completion(
               prompt=schema_prompt,
               system_message=system_message,
               temperature=0.3
           )
           
           try:
               start_idx = response.find('{')
               end_idx = response.rfind('}') + 1
               if start_idx >= 0 and end_idx > start_idx:
                   json_str = response[start_idx:end_idx]
                   return json.loads(json_str)
               raise ValueError("No valid JSON found in response")
           except (json.JSONDecodeError, ValueError) as e:
               self.logger.error(f"Failed to parse JSON response: {e}")
               raise ValueError("Invalid JSON response from model")

       except Exception as e:
           self.logger.error(f"Error getting structured completion: {str(e)}")
           raise

   def analyze_cv(self, cv_text: str) -> Dict:
       schema = {
           "skills": ["list of skills"],
           "experience_years": "number",
           "key_achievements": ["list of achievements"],
           "missing_elements": ["list of missing important elements"],
           "improvement_suggestions": ["list of suggestions"]
       }
       
       system_message = "You are an expert CV analyzer. Provide analysis in valid JSON format."
       
       prompt = (
           "Analyze the following CV content and provide structured feedback. "
           "Focus on key skills, experience, achievements, and potential improvements.\n\n"
           f"CV Content:\n{cv_text}"
       )
       
       return self.get_structured_completion(prompt, schema, system_message)

   def match_job(self, cv_text: str, job_description: str) -> Dict:
       schema = {
           "match_percentage": "number between 0 and 100",
           "matching_skills": ["list of matching skills"],
           "missing_skills": ["list of required skills not found in CV"],
           "recommendations": ["list of recommendations to improve match"]
       }
       
       system_message = "You are an expert ATS system. Provide analysis in valid JSON format."
       
       prompt = (
           "Compare the following CV against the job description and provide matching analysis.\n\n"
           f"CV:\n{cv_text}\n\n"
           f"Job Description:\n{job_description}"
       )
       
       return self.get_structured_completion(prompt, schema, system_message)