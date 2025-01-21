# test_text_analyzer.py

import unittest
import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from utils.text_analyzer import TextAnalyzer

class TestTextAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TextAnalyzer()
        
        self.test_cv = """
        Professional Experience

        Senior Software Engineer | Tech Corp
        - Developed and implemented Python applications using Django framework
        - Managed PostgreSQL databases and AWS cloud infrastructure
        
        Skills
        - Programming: Python, Java, JavaScript
        - Frameworks: Django, React
        - Databases: PostgreSQL, MongoDB
        """

    def test_preprocess_text(self):
        text = "Hello, World! This is a TEST."
        processed = self.analyzer.preprocess_text(text)
        expected = "hello, world this is a test"
        self.assertEqual(processed, expected)

    def test_extract_keywords(self):
        test_text = """
        I developed and implemented Python applications and managed large databases.
        Experienced with React and MongoDB deployments.
        """
        
        keywords = self.analyzer.extract_keywords(test_text)
        
        # Technical terms check
        technical_found = any(tech in keywords['technical_terms'] 
                            for tech in ['python', 'react', 'mongodb'])
        self.assertTrue(technical_found, f"Technical terms not found in {keywords['technical_terms']}")
        
        # Action verbs check
        action_verbs_found = any(verb in keywords['action_verbs'] 
                               for verb in ['develop', 'implement', 'manage'])
        self.assertTrue(action_verbs_found, 
                       f"Action verbs not found in {keywords['action_verbs']}")

    def test_analyze_content(self):
        analysis = self.analyzer.analyze_content(self.test_cv)
        
        self.assertIn('word_count', analysis)
        self.assertIn('sentence_count', analysis)
        self.assertIn('avg_sentence_length', analysis)
        self.assertIn('keyword_richness', analysis)
        
        self.assertGreater(analysis['word_count'], 0)
        self.assertGreater(analysis['keyword_richness'], 0)

    def test_extract_sections(self):
        sections = self.analyzer.extract_sections(self.test_cv)
        
        self.assertIn('experience', sections)
        self.assertIn('skills', sections)
        
        self.assertIn('Python', sections['skills'])
        self.assertIn('Engineer', sections['experience'])

if __name__ == '__main__':
    unittest.main()