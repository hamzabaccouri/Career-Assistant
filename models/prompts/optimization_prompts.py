# models/prompts/optimization_prompts.py

class OptimizationPrompts:
    """
    Prompts for optimizing CV and Cover Letter
    """
    
    CV_OPTIMIZATION = """
    Optimize the following CV for the specified job:
    
    Original CV:
    {cv_text}
    
    Job Description:
    {job_description}
    
    Current Match Score: {match_score}
    Missing Keywords: {missing_keywords}
    
    Optimize for:
    1. ATS compatibility
    2. Keyword optimization
    3. Achievement highlighting
    4. Skill alignment
    
    Provide optimized content in JSON format:
    {
        "optimized_cv": "string containing optimized CV text",
        "changes_made": ["list of changes made"],
        "keywords_added": ["list of keywords added"],
        "format_improvements": ["list of format improvements"]
    }
    """
    
    LETTER_OPTIMIZATION = """
    Optimize the cover letter for maximum impact:
    
    Original Letter:
    {letter_text}
    
    Job Description:
    {job_description}
    
    Company Name: {company_name}
    
    Optimize for:
    1. Job relevance
    2. Company alignment
    3. Achievement emphasis
    4. Professional impact
    
    Provide optimized content in JSON format:
    {
        "optimized_letter": "string containing optimized letter text",
        "improvements_made": ["list of improvements"],
        "company_specific_elements": ["list of company-specific content"],
        "personalization_elements": ["list of personalized elements"]
    }
    """
    
    ATS_OPTIMIZATION = """
    Optimize the CV for ATS compatibility:
    
    Original CV:
    {cv_text}
    
    ATS Issues:
    {ats_issues}
    
    Required Keywords:
    {required_keywords}
    
    Provide optimization in JSON format:
    {
        "optimized_content": "string containing ATS-optimized CV",
        "format_changes": ["list of format changes"],
        "keyword_changes": ["list of keyword optimizations"],
        "structure_changes": ["list of structural changes"],
        "verification_steps": ["list of verification steps"]
    }
    """

    SECTION_OPTIMIZATION = """
    Optimize specific CV sections:
    
    Section Content:
    {section_content}
    
    Section Type: {section_type}
    Optimization Goals: {optimization_goals}
    
    Provide optimized section in JSON format:
    {
        "optimized_section": "string containing optimized section",
        "improvements": ["list of improvements made"],
        "key_elements": ["list of key elements highlighted"],
        "format_suggestions": ["list of format suggestions"]
    }
    """