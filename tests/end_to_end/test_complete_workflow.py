import unittest
import sys
from pathlib import Path
import os
from datetime import datetime
import logging

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from agents.primary_agents.cv_analyzer import CVAnalyzer
from agents.primary_agents.job_analyzer import JobAnalyzer
from agents.primary_agents.ats_optimizer import ATSOptimizer
from agents.primary_agents.cv_matcher import CVMatcher
from agents.primary_agents.letter_writer import LetterWriter
from agents.coordinator import Coordinator
from utils.document_processor import DocumentProcessor

class TestCompleteWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        cls.logger = logging.getLogger('EndToEndTest')
        
        # Initialize all components
        cls.doc_processor = DocumentProcessor()
        cls.cv_analyzer = CVAnalyzer()
        cls.job_analyzer = JobAnalyzer()
        cls.ats_optimizer = ATSOptimizer()
        cls.cv_matcher = CVMatcher()
        cls.letter_writer = LetterWriter()
        cls.coordinator = Coordinator()
        
        # Set up test files directory
        cls.test_files_dir = os.path.abspath(os.path.join(project_root, "test_files"))
        
        if not os.path.exists(cls.test_files_dir):
            raise FileNotFoundError(f"Test files directory not found: {cls.test_files_dir}")
        
        # Find all test files
        cls.test_files = cls._find_test_files()
        cls.logger.info(f"Found test files: {cls.test_files}")
        
        if not cls.test_files['pdf'] and not cls.test_files['docx']:
            raise FileNotFoundError("No PDF or DOCX files found in test directory")
        
        # Sample job description for testing
        cls.job_description = """
        Senior Data Scientist Position
        
        Requirements:
        - 5+ years experience in Data Science and Machine Learning
        - Strong Python programming skills
        - Experience with Deep Learning frameworks
        - Team leadership experience
        - PhD or equivalent experience
        
        Responsibilities:
        - Lead ML projects
        - Develop and deploy ML models
        - Mentor junior data scientists
        - Collaborate with cross-functional teams
        """

    @classmethod
    def _find_test_files(cls) -> dict:
        """Find all test files in the test directory"""
        test_files = {
            'pdf': [],
            'docx': []
        }
        
        cls.logger.info(f"Scanning directory: {cls.test_files_dir}")
        for file in os.listdir(cls.test_files_dir):
            file_path = os.path.join(cls.test_files_dir, file)
            if not os.path.isfile(file_path):
                continue
                
            if file.lower().endswith('.pdf'):
                test_files['pdf'].append(file_path)
                cls.logger.info(f"Found PDF: {file}")
            elif file.lower().endswith('.docx'):
                test_files['docx'].append(file_path)
                cls.logger.info(f"Found DOCX: {file}")
        
        return test_files

    def _process_cv_workflow(self, cv_path: str) -> None:
        """Run the complete workflow for a single CV"""
        self.logger.info(f"Processing CV: {cv_path}")
        
        # 1. Process CV document
        cv_result = self.doc_processor.process_document(cv_path)
        self.assertTrue(cv_result['success'])
        cv_text = cv_result['content']
        self.assertIsNotNone(cv_text)
        
        # 2. Analyze job description
        job_analysis = self.job_analyzer.analyze_job(self.job_description)
        self.assertIsNotNone(job_analysis)
        
        # 3. Analyze CV
        cv_analysis = self.cv_analyzer.analyze_cv(cv_text)
        self.assertIsNotNone(cv_analysis)
        
        # 4. Match CV with job
        match_result = self.cv_matcher.match_cv_to_job(cv_text, self.job_description)
        self.assertIsNotNone(match_result)
        
        # 5. Optimize CV
        optimization_result = self.ats_optimizer.optimize_cv(cv_text, self.job_description)
        self.assertIsNotNone(optimization_result)
        
        # 6. Generate cover letter
        letter_result = self.letter_writer.generate_cover_letter(
            cv_text,
            self.job_description,
            "TechCorp"
        )
        self.assertIsNotNone(letter_result)
        
        # 7. Final quality assessment
        quality_result = self.coordinator.assess_application_quality(
            cv_text=optimization_result['optimized_cv'],
            letter_text=letter_result['letter'],
            job_description=self.job_description,
            company_name="TechCorp",
            industry="Technology"
        )
        
        self.assertIsNotNone(quality_result)
        self.assertIn('overall_quality_score', quality_result)
        
        # Log results
        self.logger.info(f"Results for {os.path.basename(cv_path)}:")
        self.logger.info(f"Match Score: {match_result['overall_match']['score']}")
        self.logger.info(f"Quality Score: {quality_result['overall_quality_score']}")

    def test_pdf_files(self):
        """Test workflow with all PDF files"""
        if not self.test_files['pdf']:
            self.logger.warning("No PDF files found to test")
            return
            
        for pdf_path in self.test_files['pdf']:
            with self.subTest(pdf_file=os.path.basename(pdf_path)):
                try:
                    self._process_cv_workflow(pdf_path)
                except Exception as e:
                    self.logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
                    raise

    def test_docx_files(self):
        """Test workflow with all DOCX files"""
        if not self.test_files['docx']:
            self.logger.warning("No DOCX files found to test")
            return
            
        for docx_path in self.test_files['docx']:
            with self.subTest(docx_file=os.path.basename(docx_path)):
                try:
                    self._process_cv_workflow(docx_path)
                except Exception as e:
                    self.logger.error(f"Error processing DOCX {docx_path}: {str(e)}")
                    raise

    def test_compare_formats(self):
        """Compare results between different file formats"""
        if not (self.test_files['pdf'] and self.test_files['docx']):
            self.logger.warning("Need both PDF and DOCX files for format comparison")
            return
            
        self.logger.info("Starting format comparison test")
        
        try:
            # Process one file of each type
            pdf_result = self.doc_processor.process_document(self.test_files['pdf'][0])
            docx_result = self.doc_processor.process_document(self.test_files['docx'][0])
            
            # Basic checks
            self.assertTrue(pdf_result['success'])
            self.assertTrue(docx_result['success'])
            self.assertIsNotNone(pdf_result['content'])
            self.assertIsNotNone(docx_result['content'])
            
            # Log comparison results
            self.logger.info("Format comparison completed successfully")
            self.logger.info(f"PDF content length: {len(pdf_result['content'])}")
            self.logger.info(f"DOCX content length: {len(docx_result['content'])}")
            
        except Exception as e:
            self.logger.error(f"Error in format comparison: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main(verbosity=2)