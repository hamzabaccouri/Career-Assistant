import unittest
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from utils.ats_rules import ATSRules

class TestATSRules(unittest.TestCase):
    def setUp(self):
        """Initialize ATSRules for each test"""
        self.ats_rules = ATSRules()

    def test_format_validation(self):
        """Test format validation with various inputs"""
        # Test valid PDF format
        result = self.ats_rules.validate_format('.pdf', 5)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['issues']), 0)
        
        # Test valid DOCX format
        result = self.ats_rules.validate_format('.docx', 5)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['issues']), 0)
        
        # Test invalid format
        result = self.ats_rules.validate_format('.jpg', 5)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['issues']), 0)
        
        # Test oversized file
        result = self.ats_rules.validate_format('.pdf', 15)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['issues']), 0)

    def test_structure_validation(self):
        """Test structure validation with various section combinations"""
        # Test standard section titles
        standard_sections = [
            'Contact Information',
            'Professional Experience',
            'Education',
            'Technical Skills'
        ]
        result = self.ats_rules.validate_structure(standard_sections)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['issues']), 0)
        
        # Test alternative section titles
        alternative_sections = [
            'Personal Information',
            'Work History',
            'Academic Background',
            'Core Competencies'
        ]
        result = self.ats_rules.validate_structure(alternative_sections)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['issues']), 0)
        
        # Test missing required sections
        incomplete_sections = [
            'Contact Information',
            'Education'
        ]
        result = self.ats_rules.validate_structure(incomplete_sections)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['issues']), 0)
        
        # Test case insensitivity
        mixed_case_sections = [
            'CONTACT INFORMATION',
            'Professional experience',
            'Education',
            'SKILLS'
        ]
        result = self.ats_rules.validate_structure(mixed_case_sections)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['issues']), 0)

    def test_optimization_guidelines(self):
        """Test the completeness of optimization guidelines"""
        guidelines = self.ats_rules.get_optimization_guidelines()
        
        # Check all guideline categories exist
        self.assertIn('format_guidelines', guidelines)
        self.assertIn('structure_guidelines', guidelines)
        self.assertIn('content_guidelines', guidelines)
        
        # Check guidelines are not empty
        self.assertGreater(len(guidelines['format_guidelines']), 0)
        self.assertGreater(len(guidelines['structure_guidelines']), 0)
        self.assertGreater(len(guidelines['content_guidelines']), 0)
        
        # Check specific guideline content
        format_guidelines = '\n'.join(guidelines['format_guidelines'])
        self.assertIn('pdf', format_guidelines.lower())
        self.assertIn('font', format_guidelines.lower())
        
        content_guidelines = '\n'.join(guidelines['content_guidelines'])
        self.assertIn('bullet points', content_guidelines.lower())

if __name__ == '__main__':
    unittest.main()