from typing import Dict, List, Optional, Any
import openai
from openai import OpenAI
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIHandler:
    def __init__(self, model: str = "gpt-4o-mini"):
        self._setup_logger()
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.model = model
        
        self.model_configs = {
            'gpt-4o-mini': {
                'max_tokens': 4000,
                'temperature': 0.7,
            },
            'gpt-4': {
                'max_tokens': 4000,
                'temperature': 0.7,
            },
            'gpt-3.5-turbo': {
                'max_tokens': 2000,
                'temperature': 0.7,
            }
        }
        
        self.logger.info(f"Initialized OpenAI handler with model: {model}")

    def _setup_logger(self):
        self.logger = logging.getLogger('OpenAIHandler')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/openai_handler_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_completion(self, 
                      prompt: str, 
                      system_message: Optional[str] = None,
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None) -> str:
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            config = self.model_configs.get(self.model, {})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or config.get('temperature', 0.7),
                max_tokens=max_tokens or config.get('max_tokens', 2000)
            )
            
            self.logger.info(f"Successfully got completion for prompt: {prompt[:100]}...")
            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error getting completion: {str(e)}")
            raise

    def get_structured_completion(self, 
                              prompt: str,
                              output_schema: Dict,
                              system_message: Optional[str] = None) -> Dict:
        try:
            # Enhanced prompt to ensure valid JSON response
            schema_prompt = (
                f"{prompt}\n\n"
                "Important: Provide your response in valid JSON format following this schema:\n"
                f"{json.dumps(output_schema, indent=2)}\n"
                "Ensure the response is a properly formatted JSON object with no trailing commas or comments."
            )
        
            if not system_message:
                system_message = "You are a helpful assistant that always responds with valid JSON matching the requested schema."
        
            response = self.get_completion(
                prompt=schema_prompt,
                system_message=system_message,
                temperature=0.1  # Lower temperature for more consistent formatting
            )
        
            # Clean and parse the response
            try:
                # Remove any potential markdown code blocks
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                
                cleaned_response = cleaned_response.strip()
            
                # Try to parse JSON
                structured_response = json.loads(cleaned_response)
            
                # Validate against schema
                for key in output_schema:
                    if key not in structured_response:
                        self.logger.warning(f"Missing required key in response: {key}")
                        structured_response[key] = [] if isinstance(output_schema[key], list) else ""
            
                return structured_response
            
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {str(e)}")
                self.logger.debug(f"Raw response: {response}")
            
                # Attempt fallback with more explicit prompt
                fallback_prompt = (
                    f"{prompt}\n\n"
                    "CRITICAL: Your response MUST be a valid JSON object. "
                    "Do not include any additional text, markdown, or explanations. "
                    f"Use exactly this structure:\n{json.dumps(output_schema, indent=2)}"
                )
            
                response = self.get_completion(
                    prompt=fallback_prompt,
                    system_message="You must respond with only valid JSON matching the schema.",
                    temperature=0.0
                )
            
                try:
                    return json.loads(response.strip())
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse JSON even after fallback")
                    # Return empty schema-compliant response
                    return {k: [] if isinstance(v, list) else "" for k, v in output_schema.items()}

        except Exception as e:
            self.logger.error(f"Error getting structured completion: {str(e)}")
            return {k: [] if isinstance(v, list) else "" for k, v in output_schema.items()}

    def analyze_cv(self, cv_text: str) -> Dict:
        schema = {
            "skills": ["list of skills"],
            "experience_years": "number",
            "key_achievements": ["list of achievements"],
            "missing_elements": ["list of missing important elements"],
            "improvement_suggestions": ["list of suggestions"]
        }
        
        prompt = (
            "Analyze the following CV content and provide structured feedback. "
            "Focus on key skills, experience, achievements, and potential improvements.\n\n"
            f"CV Content:\n{cv_text}"
        )
        
        return self.get_structured_completion(prompt, schema)

    def match_job(self, cv_text: str, job_description: str) -> Dict:
        schema = {
            "match_percentage": "number between 0 and 100",
            "matching_skills": ["list of matching skills"],
            "missing_skills": ["list of required skills not found in CV"],
            "recommendations": ["list of recommendations to improve match"]
        }
        
        prompt = (
            "Compare the following CV against the job description and provide matching analysis.\n\n"
            f"CV:\n{cv_text}\n\n"
            f"Job Description:\n{job_description}"
        )
        
        return self.get_structured_completion(prompt, schema)