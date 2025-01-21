from typing import Dict, List, Union
import logging
import os
from datetime import datetime

class ATSRules:
    """
    Manages ATS (Applicant Tracking System) rules and guidelines
    for CV optimization and validation.
    """
    
    def __init__(self):
        self._setup_logger()
        
        # Format rules
        self.format_rules = {
            'allowed_formats': ['.pdf', '.docx'],
            'max_file_size_mb': 10,
            'recommended_fonts': ['Arial', 'Calibri', 'Times New Roman', 'Helvetica'],
            'min_font_size': 10,
            'max_font_size': 12
        }
        
        # Structure rules with section variations
        self.structure_rules = {
            'required_sections': [
                'contact_information',
                'professional_experience',
                'education',
                'skills'
            ],
            'recommended_sections': [
                'summary',
                'certifications',
                'languages',
                'projects'
            ],
            'section_titles': {
                'contact': [
                    'contact',
                    'contact information',
                    'personal information',
                    'personal details',
                    'personal info'
                ],
                'experience': [
                    'experience',
                    'work experience',
                    'professional experience',
                    'work history',
                    'employment history',
                    'professional background'
                ],
                'education': [
                    'education',
                    'academic background',
                    'qualifications',
                    'academic qualifications',
                    'educational background'
                ],
                'skills': [
                    'skills',
                    'technical skills',
                    'competencies',
                    'key skills',
                    'core competencies',
                    'professional skills'
                ]
            }
        }
        
        # Content rules
        self.content_rules = {
            'max_pages': 2,
            'max_bullets_per_job': 6,
            'max_characters_per_bullet': 100,
            'forbidden_elements': [
                'images',
                'tables',
                'text boxes',
                'headers',
                'footers',
                'columns'
            ],
            'recommended_keywords_per_section': {
                'skills': 10,
                'experience': 5
            }
        }

    def _setup_logger(self):
        """Configure logging"""
        self.logger = logging.getLogger('ATSRules')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler(
            f'logs/ats_rules_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)

    def validate_format(self, file_format: str, file_size_mb: float) -> Dict[str, Union[bool, List[str]]]:
        """
        Validate document format against ATS rules.
        
        Args:
            file_format (str): The file extension (e.g., '.pdf')
            file_size_mb (float): File size in megabytes
            
        Returns:
            Dict containing validation result and any issues found
        """
        self.logger.info(f"Validating format: {file_format}, size: {file_size_mb}MB")
        issues = []
        
        if file_format.lower() not in self.format_rules['allowed_formats']:
            issues.append(f"Unsupported format. Use {', '.join(self.format_rules['allowed_formats'])}")
            
        if file_size_mb > self.format_rules['max_file_size_mb']:
            issues.append(f"File too large. Maximum size is {self.format_rules['max_file_size_mb']}MB")
        
        valid = len(issues) == 0
        self.logger.info(f"Format validation completed. Valid: {valid}, Issues: {issues}")
        
        return {
            'valid': valid,
            'issues': issues
        }

    def validate_structure(self, sections: List[str]) -> Dict[str, Union[bool, List[str]]]:
        """
        Validate CV structure against ATS requirements.
        
        Args:
            sections (List[str]): List of section titles in the CV
            
        Returns:
            Dict containing validation result and any issues found
        """
        self.logger.info(f"Validating structure with sections: {sections}")
        issues = []
        
        # Normalize sections for comparison
        normalized_sections = [self._normalize_section_title(s) for s in sections]
        self.logger.debug(f"Normalized sections: {normalized_sections}")
        
        # Check each required section
        for required in self.structure_rules['required_sections']:
            # Get section type and variants
            section_type = next(
                (stype for stype, variants in self.structure_rules['section_titles'].items() 
                 if required.replace('_', '') in stype),
                None
            )
            
            if section_type:
                # Get all possible variants for this section
                variants = [self._normalize_section_title(v) 
                          for v in self.structure_rules['section_titles'][section_type]]
                
                # Check if any variant matches
                if not any(any(variant in section for section in normalized_sections) 
                          for variant in variants):
                    issues.append(f"Missing required section: {required}")
                    self.logger.warning(f"Missing required section: {required}")
                else:
                    self.logger.debug(f"Found required section: {required}")
        
        valid = len(issues) == 0
        self.logger.info(f"Structure validation completed. Valid: {valid}, Issues: {issues}")
        
        return {
            'valid': valid,
            'issues': issues
        }

    def _normalize_section_title(self, title: str) -> str:
        """
        Normalize section title for comparison.
        
        Args:
            title (str): Section title to normalize
            
        Returns:
            str: Normalized section title
        """
        # Remove special characters and extra spaces
        normalized = ''.join(c.lower() for c in title if c.isalnum() or c.isspace())
        normalized = ' '.join(normalized.split())
        
        # Handle common abbreviations and variations
        replacements = {
            'edu': 'education',
            'academic': 'education',
            'qualification': 'education',
            'exp': 'experience',
            'professional': 'experience',
            'employment': 'experience',
            'work': 'experience',
            'comp': 'competencies',
            'tech': 'technical'
        }
        
        for old, new in replacements.items():
            if old in normalized:
                normalized = normalized.replace(old, new)
        
        return normalized

    def get_optimization_guidelines(self) -> Dict[str, List[str]]:
        """
        Get comprehensive ATS optimization guidelines.
        
        Returns:
            Dict containing categorized optimization guidelines
        """
        return {
            'format_guidelines': [
                f"Use approved file formats: {', '.join(self.format_rules['allowed_formats'])}",
                f"Keep file size under {self.format_rules['max_file_size_mb']}MB",
                f"Use standard fonts: {', '.join(self.format_rules['recommended_fonts'])}",
                f"Font size between {self.format_rules['min_font_size']} and {self.format_rules['max_font_size']}"
            ],
            'structure_guidelines': [
                "Include all required sections",
                "Use standard section titles",
                "Avoid complex formatting",
                f"Maximum {self.content_rules['max_pages']} pages",
                "Ensure clear section headings"
            ],
            'content_guidelines': [
                f"Maximum {self.content_rules['max_bullets_per_job']} bullet points per job",
                f"Keep bullet points under {self.content_rules['max_characters_per_bullet']} characters",
                f"Avoid: {', '.join(self.content_rules['forbidden_elements'])}",
                "Use industry-standard keywords",
                "Include measurable achievements"
            ]
        }
