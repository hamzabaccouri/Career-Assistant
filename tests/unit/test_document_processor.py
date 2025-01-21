import unittest
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from utils.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()
        self.test_files_dir = os.path.join(project_root, "test_files")
        
    def test_pdf_processing(self):
        """Test PDF processing"""
        pdf_path = os.path.join(self.test_files_dir, "CV_Data_Scientist_Hamza.pdf")
        if os.path.exists(pdf_path):
            result = self.processor.process_document(pdf_path)
            self.assertTrue(result['success'])
            self.assertIsNotNone(result['content'])
            self.assertIsInstance(result['metadata'], dict)
            self.assertIn('pages', result['metadata'])
            print(f"PDF Content preview: {result['content'][:200]}")
            
    def test_docx_processing(self):
        """Test DOCX processing"""
        docx_path = os.path.join(self.test_files_dir, "Dossier_Technique_Hamza_Baccouri.docx")
        if os.path.exists(docx_path):
            result = self.processor.process_document(docx_path)
            self.assertTrue(result['success'])
            self.assertIsNotNone(result['content'])
            self.assertIsInstance(result['metadata'], dict)
            self.assertIn('paragraphs', result['metadata'])
            print(f"DOCX Content preview: {result['content'][:200]}")

if __name__ == '__main__':
    unittest.main()