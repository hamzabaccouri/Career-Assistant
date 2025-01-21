import streamlit as st
import os
import io
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from utils.document_processor import DocumentProcessor
from agents.primary_agents.cv_analyzer import CVAnalyzer
from agents.primary_agents.job_analyzer import JobAnalyzer
from agents.primary_agents.cv_matcher import CVMatcher
from agents.primary_agents.ats_optimizer import ATSOptimizer
from agents.primary_agents.letter_writer import LetterWriter
from agents.coordinator import Coordinator

class CareerAssistantApp:
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.cv_analyzer = CVAnalyzer()
        self.job_analyzer = JobAnalyzer()
        self.cv_matcher = CVMatcher()
        self.ats_optimizer = ATSOptimizer()
        self.letter_writer = LetterWriter()
        self.coordinator = Coordinator()
        
        if 'cv_text' not in st.session_state:
            st.session_state.cv_text = None
        if 'job_text' not in st.session_state:
            st.session_state.job_text = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'analysis_started' not in st.session_state:
            st.session_state.analysis_started = False

    def run(self):
        st.title("Career Application Assistant")
        
        with st.sidebar:
            st.header("Input Section")
            
            cv_file = st.file_uploader(
                "Upload your CV (PDF or DOCX)",
                type=['pdf', 'docx']
            )
            
            if cv_file:
                try:
                    file_content = cv_file.read()
                    with open(f"temp_{cv_file.name}", "wb") as f:
                        f.write(file_content)
                    
                    result = self.doc_processor.process_document(f"temp_{cv_file.name}")
                    if result['success']:
                        st.session_state.cv_text = result['content']
                        st.success("CV uploaded successfully!")
                    else:
                        st.error("Error processing CV")
                    
                    os.remove(f"temp_{cv_file.name}")
                    
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
            
            st.header("Job Description")
            job_description = st.text_area(
                "Paste the job description here",
                height=300
            )
            if job_description:
                st.session_state.job_text = job_description

            if st.session_state.cv_text and st.session_state.job_text:
                if st.button("Start Analysis", type="primary"):
                    st.session_state.analysis_started = True
                    with st.spinner("Analyzing documents..."):
                        st.session_state.analysis_results = self._perform_analysis()
                    st.success("Analysis completed!")

        if st.session_state.analysis_started and st.session_state.analysis_results:
            tab1, tab2, tab3, tab4 = st.tabs([
                "ATS Analysis", 
                "Match Analysis",
                "CV Optimization",
                "Cover Letter"
            ])
            
            with tab1:
                self._show_ats_analysis()
            with tab2:
                self._show_match_analysis()
            with tab3:
                self._show_cv_optimization()
            with tab4:
                self._show_cover_letter()
        
        else:
            st.info("Please upload your CV, provide a job description, and click 'Start Analysis' to begin.")

    def _perform_analysis(self):
        try:
            job_analysis = self.job_analyzer.analyze_job(st.session_state.job_text)
            cv_analysis = self.cv_analyzer.analyze_cv(st.session_state.cv_text)
            match_analysis = self.cv_matcher.match_cv_to_job(
                st.session_state.cv_text,
                st.session_state.job_text
            )
            optimization = self.ats_optimizer.optimize_cv(
                st.session_state.cv_text,
                st.session_state.job_text
            )
            ats_quality = self.coordinator.assess_application_quality(
                cv_text=st.session_state.cv_text,
                letter_text="",
                job_description=st.session_state.job_text,
                company_name="Company Name"
            )
            
            return {
                'job_analysis': job_analysis,
                'cv_analysis': cv_analysis,
                'match_analysis': match_analysis,
                'optimization': optimization,
                'ats_quality': ats_quality
            }
            
        except Exception as e:
            st.error(f"Error performing analysis: {str(e)}")
            return {}

    def _show_ats_analysis(self):
        st.header("ATS Compatibility Analysis")
        
        results = st.session_state.analysis_results
        if not results or 'ats_quality' not in results:
            st.warning("No ATS analysis results available")
            return
        
        ats_score = results['ats_quality'].get('ats_score', 0)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("ATS Compatibility Score", f"{ats_score}%")
        
        st.subheader("ATS Recommendations")
        ats_recs = results['ats_quality'].get('improvement_recommendations', {})
        
        if high_priority := ats_recs.get('high_priority', []):
            st.error("Critical Improvements Needed:")
            for rec in high_priority:
                st.write(f"• {rec}")
        
        if medium_priority := ats_recs.get('medium_priority', []):
            st.warning("Suggested Improvements:")
            for rec in medium_priority:
                st.write(f"• {rec}")
                
        if format_issues := results['ats_quality'].get('format_issues', []):
            st.info("Format Improvements:")
            for issue in format_issues:
                st.write(f"• {issue}")

    def _show_match_analysis(self):
        st.header("Job Match Analysis")
        
        results = st.session_state.analysis_results
        if not results or 'match_analysis' not in results:
            st.warning("No match analysis results available")
            return
        
        match_info = results['match_analysis']
        
        st.metric(
            "Overall Match Score",
            f"{match_info['overall_match']['score']}%"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Skills Match", f"{match_info['skills_match']['score']}%")
        with col2:
            st.metric("Experience Match", f"{match_info['experience_match']['score']}%")
        with col3:
            st.metric("Education Match", f"{match_info['education_match']['score']}%")
        
        st.subheader("Missing Requirements")
        missing_skills = match_info['skills_match'].get('missing_required', [])
        if missing_skills:
            st.write("Required skills not found in your CV:")
            for skill in missing_skills:
                st.write(f"• {skill}")

    def _show_cv_optimization(self):
        st.header("CV Optimization")
        
        results = st.session_state.analysis_results
        if not results or 'optimization' not in results:
            st.warning("No optimization results available")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original CV")
            st.text_area("Original Content", st.session_state.cv_text, height=400)
        
        with col2:
            st.subheader("Optimized CV")
            optimized_text = results['optimization'].get('optimized_cv', '')
            st.text_area("Optimized Content", optimized_text, height=400)
        
        st.subheader("Download Options")
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("Copy Optimized Text"):
                st.code(optimized_text)
                st.success("Text copied! You can now paste it into your preferred editor.")
        
        with col4:
            st.download_button(
                label="Download as Text File",
                data=optimized_text,
                file_name=f"optimized_cv_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

    def _show_cover_letter(self):
        st.header("Cover Letter Generator")
        
        company_name = st.text_input("Company Name")
        
        if st.button("Generate Cover Letter"):
            with st.spinner("Generating cover letter..."):
                letter_result = self.letter_writer.generate_cover_letter(
                    st.session_state.cv_text,
                    st.session_state.job_text,
                    company_name or "Company Name"
                )
                
                st.subheader("Generated Cover Letter")
                st.text_area("Cover Letter Content", letter_result['letter'], height=400)
                
                st.download_button(
                    label="Download Cover Letter",
                    data=letter_result['letter'],
                    file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    app = CareerAssistantApp()
    app.run()