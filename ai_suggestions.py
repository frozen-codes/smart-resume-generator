"""
AI Suggestions Module for Resume Generator
Provides AI-powered suggestions for resume content
"""

import requests
import json
import random

# Default URL for Ollama API
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Hardcoded skill suggestions by role (fallback when Ollama is not available)
SKILL_SUGGESTIONS = {
    "software developer": [
        "Python", "JavaScript", "Java", "C#", "C++", "TypeScript", 
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask",
        "SQL", "MongoDB", "PostgreSQL", "AWS", "Docker", "Kubernetes",
        "CI/CD", "Git", "Agile Methodologies", "Problem Solving"
    ],
    "data scientist": [
        "Python", "R", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", 
        "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Data Visualization", 
        "Statistical Analysis", "Big Data", "Hadoop", "Spark", "NLP",
        "A/B Testing", "Data Mining", "Feature Engineering"
    ],
    "product manager": [
        "Product Strategy", "Market Research", "User Stories", "Agile", "Scrum",
        "Roadmapping", "Competitive Analysis", "A/B Testing", "User Experience", 
        "Product Lifecycle Management", "JIRA", "Confluence", "SQL", "Analytics",
        "Stakeholder Management", "Presentation Skills", "Prioritization"
    ],
    "designer": [
        "UI/UX Design", "Figma", "Adobe Creative Suite", "Sketch", "InVision",
        "Wireframing", "Prototyping", "Typography", "Color Theory", "Design Systems",
        "User Research", "Usability Testing", "Responsive Design", "Accessibility"
    ],
    "marketing": [
        "Digital Marketing", "Content Marketing", "SEO", "SEM", "Social Media Marketing",
        "Email Marketing", "Google Analytics", "A/B Testing", "Market Research",
        "Campaign Management", "Brand Strategy", "Adobe Analytics", "HubSpot", "CRM"
    ]
}

# Hardcoded summary suggestions by role
SUMMARY_SUGGESTIONS = {
    "software developer": [
        "Experienced software developer with a proven track record of building scalable, efficient applications.",
        "Results-driven software engineer with expertise in designing and implementing robust solutions to complex problems.",
        "Detail-oriented developer with strong analytical skills and a passion for clean, maintainable code."
    ],
    "data scientist": [
        "Data scientist with expertise in applying statistical methods and machine learning to extract actionable insights.",
        "Analytical professional skilled in transforming complex datasets into clear business recommendations.",
        "Results-oriented data scientist with experience in building predictive models that drive business decisions."
    ],
    "product manager": [
        "Strategic product manager with a proven ability to identify market opportunities and deliver successful products.",
        "User-focused product manager experienced in translating customer needs into product features and roadmaps.",
        "Results-driven product leader with expertise in managing the full product lifecycle from conception to launch."
    ],
    "designer": [
        "Creative designer with a keen eye for aesthetics and a user-centered approach to design challenges.",
        "Innovative design professional with expertise in creating intuitive, engaging user experiences.",
        "Detail-oriented designer skilled in balancing creativity with functional requirements to deliver impactful designs."
    ],
    "marketing": [
        "Strategic marketing professional with a track record of developing campaigns that increase brand awareness and drive conversion.",
        "Data-driven marketer experienced in leveraging analytics to optimize marketing strategies and ROI.",
        "Creative marketing specialist with expertise in crafting compelling narratives that resonate with target audiences."
    ]
}

# Experience bullet point suggestions by role
EXPERIENCE_SUGGESTIONS = {
    "software developer": [
        "Developed and maintained {technology} applications serving {number} users",
        "Implemented CI/CD pipeline resulting in {percentage}% reduction in deployment time",
        "Refactored legacy code base improving performance by {percentage}%",
        "Collaborated with cross-functional teams to deliver features on time and within scope",
        "Designed and implemented RESTful APIs for third-party integrations",
        "Led code reviews and mentored junior developers in best practices"
    ],
    "data scientist": [
        "Built predictive models that improved {metric} by {percentage}%",
        "Analyzed large datasets to identify patterns and trends that informed business strategy",
        "Developed automated reporting dashboards used by executive leadership",
        "Implemented A/B testing framework that optimized conversion rates",
        "Created machine learning algorithms that enhanced product recommendations",
        "Collaborated with stakeholders to translate business questions into data analysis projects"
    ],
    "product manager": [
        "Led product strategy resulting in {percentage}% increase in user engagement",
        "Managed product roadmap and prioritized features based on user feedback and business goals",
        "Collaborated with engineering teams to deliver products on schedule and within budget",
        "Conducted market research to identify customer needs and competitive positioning",
        "Defined and tracked KPIs to measure product success and inform iterations",
        "Presented product vision and strategy to executive leadership"
    ]
}

def get_skill_suggestions(job_role):
    """
    Get skill suggestions based on job role.
    Falls back to hardcoded suggestions if Ollama is not available.
    
    Args:
        job_role: The job role to get skills for
    
    Returns:
        list: List of suggested skills
    """
    # Normalize job role to match our keys
    job_role = job_role.lower()
    
    # Find the closest match in our hardcoded skills
    closest_role = "software developer"  # Default role
    for role in SKILL_SUGGESTIONS:
        if role in job_role or job_role in role:
            closest_role = role
            break
    
    # Try to get suggestions from Ollama first
    try:
        ai_suggestions = get_suggestions_from_ollama(
            f"List 10 important professional skills for a {job_role} role. " +
            "Provide a comma-separated list of technical and soft skills."
        )
        
        if ai_suggestions:
            # Parse the comma-separated list
            skills = [s.strip() for s in ai_suggestions.split(',')]
            # Remove any empty items
            skills = [s for s in skills if s]
            # Limit to 15 skills
            return skills[:15]
    except:
        # If Ollama fails, fall back to hardcoded suggestions
        pass
    
    # Use our hardcoded fallback
    return random.sample(SKILL_SUGGESTIONS.get(closest_role, SKILL_SUGGESTIONS["software developer"]), 
                         min(12, len(SKILL_SUGGESTIONS.get(closest_role, SKILL_SUGGESTIONS["software developer"]))))

def get_summary_suggestion(job_role, years_experience=None):
    """
    Get a summary suggestion based on job role and experience.
    
    Args:
        job_role: The job role
        years_experience: Optional years of experience
    
    Returns:
        str: A suggested summary
    """
    # Normalize job role
    job_role = job_role.lower()
    
    # Try to get suggestions from Ollama first
    experience_text = f" with {years_experience} years of experience" if years_experience else ""
    try:
        ai_suggestion = get_suggestions_from_ollama(
            f"Write a concise, powerful professional summary for a {job_role}{experience_text}. " +
            "Keep it to 2-3 sentences highlighting key strengths."
        )
        
        if ai_suggestion:
            return ai_suggestion
    except:
        # If Ollama fails, fall back to hardcoded suggestions
        pass
    
    # Find the closest match in our hardcoded summaries
    for role in SUMMARY_SUGGESTIONS:
        if role in job_role:
            summaries = SUMMARY_SUGGESTIONS[role]
            return random.choice(summaries)
    
    # Default to software developer if no match
    return random.choice(SUMMARY_SUGGESTIONS["software developer"])

def get_experience_bullet_points(job_role, company=None, count=3):
    """
    Get experience bullet point suggestions.
    
    Args:
        job_role: The job role
        company: Optional company name to include
        count: Number of bullet points to generate
    
    Returns:
        list: List of bullet point suggestions
    """
    # Normalize job role
    job_role = job_role.lower()
    
    # Try to get suggestions from Ollama first
    company_text = f" at {company}" if company else ""
    try:
        ai_suggestion = get_suggestions_from_ollama(
            f"Generate {count} concise, achievement-oriented bullet points for a resume " +
            f"for a {job_role}{company_text} position. Include concrete metrics and achievements " +
            "where possible. Format as a numbered list."
        )
        
        if ai_suggestion:
            # Parse the numbered list
            bullet_points = []
            for line in ai_suggestion.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line[0] == '-'):
                    bullet_points.append(line[2:].strip() if line[0].isdigit() else line[1:].strip())
            
            if bullet_points:
                return bullet_points[:count]
    except:
        # If Ollama fails, fall back to hardcoded suggestions
        pass
    
    # Find templates for the closest role
    templates = []
    for role in EXPERIENCE_SUGGESTIONS:
        if role in job_role:
            templates = EXPERIENCE_SUGGESTIONS[role]
            break
    
    # Default to software developer if no match
    if not templates:
        templates = EXPERIENCE_SUGGESTIONS["software developer"]
    
    # Generate bullet points from templates
    bullet_points = []
    sampled_templates = random.sample(templates, min(count, len(templates)))
    
    for template in sampled_templates:
        # Replace placeholders with random values
        bullet = template.replace("{technology}", random.choice(["web", "mobile", "cloud", "desktop"]))
        bullet = bullet.replace("{number}", str(random.randint(100, 10000)))
        bullet = bullet.replace("{percentage}", str(random.randint(15, 50)))
        bullet = bullet.replace("{metric}", random.choice(["accuracy", "efficiency", "sales", "retention"]))
        bullet_points.append(bullet)
    
    # Fill up to count if needed
    while len(bullet_points) < count:
        bullet_points.append(random.choice(EXPERIENCE_SUGGESTIONS["software developer"]).replace(
            "{technology}", random.choice(["web", "mobile", "cloud", "desktop"])
        ).replace(
            "{number}", str(random.randint(100, 10000))
        ).replace(
            "{percentage}", str(random.randint(15, 50))
        ).replace(
            "{metric}", random.choice(["accuracy", "efficiency", "sales", "retention"]))
        )
    
    return bullet_points

def get_suggestions_from_ollama(prompt):
    """
    Get suggestions from Ollama API
    
    Args:
        prompt: The prompt to send to Ollama
    
    Returns:
        str: The generated text or None if failed
    """
    try:
        payload = {
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        
        return None
    except:
        return None 