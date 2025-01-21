# models/prompts/analysis_prompts.py

class AnalysisPrompts:
    """
    Prompts for CV and Job Description analysis
    """
    
    # CV Analysis Prompts
    CV_ANALYSIS = """
    Analyze the following CV focusing on key professional elements:
    
    CV Content:
    {cv_text}
    
    Provide a detailed analysis in the following structure:
    1. Key skills and expertise
    2. Experience level and achievements
    3. Education and qualifications
    4. Professional strengths
    5. Areas for improvement
    
    Format the response as JSON with these keys:
    {
        "skills": ["list of key skills"],
        "experience_years": "number",
        "achievements": ["list of key achievements"],
        "education": ["list of qualifications"],
        "strengths": ["list of strengths"],
        "improvement_areas": ["list of areas to improve"]
    }
    """
    
    JOB_ANALYSIS = """
    Analyze the following job description in detail:
    
    Job Description:
    {job_description}
    
    Provide a structured analysis focusing on:
    1. Required qualifications and skills
    2. Key responsibilities
    3. Experience requirements
    4. Company culture indicators
    5. Additional preferences or requirements
    
    Format the response as JSON with these keys:
    {
        "required_skills": ["list of must-have skills"],
        "preferred_skills": ["list of nice-to-have skills"],
        "experience_required": "string describing experience requirements",
        "responsibilities": ["list of key responsibilities"],
        "company_culture": ["list of culture indicators"],
        "additional_requirements": ["list of other requirements"]
    }
    """
    
    SKILL_MATCH_ANALYSIS = """
    Analyze the match between the candidate's skills and job requirements:
    
    CV Skills:
    {cv_skills}
    
    Job Requirements:
    {job_requirements}
    
    Provide a detailed matching analysis in JSON format:
    {
        "matching_skills": ["list of matching skills"],
        "missing_skills": ["list of required skills not found"],
        "match_percentage": "number between 0 and 100",
        "skill_gap_recommendations": ["list of recommendations"]
    }
    """
    
    EXPERIENCE_ANALYSIS = """
    Analyze the candidate's experience against job requirements:
    
    Candidate Experience:
    {experience}
    
    Required Experience:
    {required_experience}
    
    Provide analysis in JSON format:
    {
        "meets_requirements": "boolean",
        "experience_match_level": "number between 0 and 100",
        "relevant_experience": ["list of relevant experiences"],
        "missing_experience": ["list of missing experience areas"],
        "recommendations": ["list of recommendations"]
    }
    """