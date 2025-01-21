# models/prompts/evaluation_prompts.py

class EvaluationPrompts:
    """
    Prompts for evaluating CV and Cover Letter quality
    """
    
    CV_QUALITY_EVALUATION = """
    Evaluate the quality of the following CV:
    
    CV Content:
    {cv_text}
    
    Industry Context:
    {industry}
    
    Evaluate based on:
    1. Content quality and relevance
    2. Professional presentation
    3. Achievement quantification
    4. Skill presentation
    5. Overall effectiveness
    
    Provide evaluation in JSON format:
    {
        "overall_score": "number between 0 and 100",
        "content_quality": {
            "score": "number between 0 and 100",
            "strengths": ["list of strengths"],
            "weaknesses": ["list of weaknesses"]
        },
        "presentation_quality": {
            "score": "number between 0 and 100",
            "issues": ["list of issues"],
            "positives": ["list of positives"]
        },
        "recommendations": ["list of recommendations"]
    }
    """
    
    LETTER_QUALITY_EVALUATION = """
    Evaluate the quality of the following cover letter:
    
    Cover Letter:
    {letter_text}
    
    Job Description:
    {job_description}
    
    Evaluate based on:
    1. Relevance to position
    2. Professional tone
    3. Company fit
    4. Customization level
    5. Overall impact
    
    Provide evaluation in JSON format:
    {
        "overall_score": "number between 0 and 100",
        "relevance_score": "number between 0 and 100",
        "tone_score": "number between 0 and 100",
        "customization_score": "number between 0 and 100",
        "strong_points": ["list of strong points"],
        "weak_points": ["list of weak points"],
        "improvement_suggestions": ["list of suggestions"]
    }
    """
    
    ATS_COMPLIANCE_CHECK = """
    Evaluate ATS compliance for this CV:
    
    CV Content:
    {cv_text}
    
    Evaluate based on:
    1. Format compliance
    2. Keyword optimization
    3. Section structure
    4. Content clarity
    
    Provide evaluation in JSON format:
    {
        "ats_score": "number between 0 and 100",
        "format_issues": ["list of format issues"],
        "keyword_optimization": {
            "score": "number between 0 and 100",
            "missing_keywords": ["list of missing keywords"]
        },
        "structure_compliance": {
            "score": "number between 0 and 100",
            "issues": ["list of structural issues"]
        },
        "recommendations": ["list of recommendations"]
    }
    """