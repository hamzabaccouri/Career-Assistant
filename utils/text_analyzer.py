# text_analyzer.py

import re
from typing import List, Dict, Union
import logging
import os
from datetime import datetime

class TextAnalyzer:
    def __init__(self):
        self._setup_logger()
        
        # Keep technical terms dictionary for reference
        self.technical_terms = {
            'programming': {
                'python', 'java', 'javascript', 'c++', 'ruby', 'php', 'scala',
                'swift', 'kotlin', 'golang', 'rust', 'typescript'
            },
            'frameworks': {
                'django', 'flask', 'fastapi', 'spring', 'react', 'angular',
                'vue', 'node.js', 'express', 'laravel', 'rails'
            },
            'databases': {
                'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis',
                'elasticsearch', 'cassandra', 'dynamodb'
            },
            'cloud': {
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
                'jenkins', 'circleci', 'gitlab'
            },
            'machine_learning': {
                'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'opencv',
                'pandas', 'numpy', 'matplotlib', 'seaborn'
            }
        }
        
        self.action_verbs = {
            'develop', 'implement', 'design', 'manage', 'lead',
            'create', 'improve', 'increase', 'reduce', 'analyze',
            'coordinate', 'achieve', 'deliver', 'launch', 'build'
        }
        
        self.logger.info("TextAnalyzer initialized successfully")

    def _setup_logger(self):
        self.logger = logging.getLogger('TextAnalyzer')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(
            f'logs/text_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s\.\,\-\']', ' ', text)
        text = re.sub(r'\.$', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract keywords using pattern matching and known terms"""
        try:
            processed_text = self.preprocess_text(text)
            words = processed_text.split()
            
            keywords = {
                'technical_terms': [],
                'action_verbs': [],
                'nouns': []
            }
            
            # Extract technical terms
            for category, terms in self.technical_terms.items():
                for word in words:
                    if word in terms:
                        keywords['technical_terms'].append(word)
            
            # Extract action verbs
            for word in words:
                if word in self.action_verbs:
                    keywords['action_verbs'].append(word)
            
            # Remove duplicates and sort
            for category in keywords:
                keywords[category] = sorted(list(set(keywords[category])))
            
            return keywords
            
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {str(e)}")
            return {
                'technical_terms': [],
                'action_verbs': [],
                'nouns': []
            }

    def analyze_content(self, text: str) -> Dict[str, Union[int, float, List[str]]]:
        """Analyze text content for basic metrics"""
        try:
            processed_text = self.preprocess_text(text)
            # Simple sentence splitting on punctuation
            sentences = [s.strip() for s in re.split(r'[.!?]+', processed_text) if s.strip()]
            words = processed_text.split()
            
            analysis = {
                'sentence_count': len(sentences),
                'word_count': len(words),
                'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
                'unique_words': len(set(words)),
                'keyword_richness': self._calculate_keyword_richness(words)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing content: {str(e)}")
            return {
                'sentence_count': 0,
                'word_count': 0,
                'avg_sentence_length': 0,
                'unique_words': 0,
                'keyword_richness': 0
            }

    def _calculate_keyword_richness(self, words: List[str]) -> float:
        """Calculate percentage of keywords in text"""
        total_words = len(words)
        if total_words == 0:
            return 0.0
            
        keyword_count = sum(1 for word in words if any(
            word in terms for terms in self.technical_terms.values()
        ) or word in self.action_verbs)
        
        return (keyword_count / total_words) * 100

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract document sections using regex patterns"""
        section_patterns = {
            'education': r'education|academic|qualifications',
            'experience': r'experience|employment|work history',
            'skills': r'skills|competencies|expertise',
            'projects': r'projects|portfolio|works',
            'contact': r'contact|personal information|details'
        }
        
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            section_found = False
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line.lower()):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found and current_section:
                current_content.append(line)
        
        # Add last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections