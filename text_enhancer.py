"""
Text Enhancer Module for Resume Generator
Provides spelling, grammar checking, and text improvement tools
"""

import re
import json
import os
import random
import string
import requests

# Try to import optional dependencies
try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False

# Ollama API URL for AI-powered enhancement
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Common spelling mistakes dictionary
COMMON_SPELLING_MISTAKES = {
    "accomodate": "accommodate",
    "acheive": "achieve",
    "accross": "across",
    "agressive": "aggressive",
    "alot": "a lot",
    "arguement": "argument",
    "assesment": "assessment",
    "basicly": "basically",
    "begining": "beginning",
    "beleive": "believe",
    "calender": "calendar",
    "catagory": "category",
    "commited": "committed",
    "completly": "completely",
    "concious": "conscious",
    "definately": "definitely",
    "dissapoint": "disappoint",
    "embarass": "embarrass",
    "enviroment": "environment",
    "excelent": "excellent",
    "explaination": "explanation",
    "familar": "familiar",
    "finaly": "finally",
    "foriegn": "foreign",
    "gaurd": "guard",
    "goverment": "government",
    "grammer": "grammar",
    "happend": "happened",
    "harrassment": "harassment",
    "immediatly": "immediately",
    "independant": "independent",
    "liason": "liaison",
    "maintainance": "maintenance",
    "millenium": "millennium",
    "neccessary": "necessary",
    "noticable": "noticeable",
    "occassion": "occasion",
    "occured": "occurred",
    "persistant": "persistent",
    "personel": "personnel",
    "plannning": "planning",
    "posession": "possession",
    "prefered": "preferred",
    "recieve": "receive",
    "reccomend": "recommend",
    "refered": "referred",
    "referance": "reference",
    "relevent": "relevant",
    "seperate": "separate",
    "succesful": "successful",
    "supercede": "supersede",
    "tommorrow": "tomorrow",
    "untill": "until"
}

# Resume power words by category
RESUME_POWER_WORDS = {
    "leadership": [
        "Achieved", "Administered", "Championed", "Delegated", "Directed", 
        "Established", "Executed", "Facilitated", "Guided", "Headed", 
        "Implemented", "Initiated", "Led", "Managed", "Orchestrated", 
        "Oversaw", "Pioneered", "Prioritized", "Spearheaded", "Steered"
    ],
    "communication": [
        "Addressed", "Articulated", "Authored", "Collaborated", "Conveyed", 
        "Convinced", "Corresponded", "Delivered", "Documented", "Edited", 
        "Influenced", "Interpreted", "Mediated", "Negotiated", "Persuaded", 
        "Presented", "Promoted", "Publicized", "Reconciled", "Translated"
    ],
    "technical": [
        "Analyzed", "Built", "Calculated", "Computed", "Constructed", 
        "Designed", "Devised", "Engineered", "Fabricated", "Installed", 
        "Maintained", "Operated", "Programmed", "Remodeled", "Repaired", 
        "Solved", "Standardized", "Streamlined", "Upgraded", "Utilized"
    ],
    "problem_solving": [
        "Adapted", "Alleviated", "Corrected", "Debugged", "Decided", 
        "Diagnosed", "Eased", "Elevated", "Examined", "Formulated", 
        "Improved", "Investigated", "Overhauled", "Reconciled", "Rectified", 
        "Redesigned", "Reengineered", "Resolved", "Revamped", "Transformed"
    ],
    "achievement": [
        "Accomplished", "Advanced", "Amplified", "Boosted", "Capitalized", 
        "Delivered", "Enhanced", "Exceeded", "Expanded", "Generated", 
        "Improved", "Maximized", "Outperformed", "Produced", "Reduced", 
        "Rejuvenated", "Renovated", "Restored", "Surpassed", "Transformed"
    ]
}

# Weak words to eliminate from resume
WEAK_WORDS = [
    "very", "really", "just", "quite", "basically", "actually", "simply", "nice",
    "good", "bad", "great", "like", "thing", "stuff", "etc", "a lot", "got", "kind of", 
    "sort of", "type of", "feel", "think", "believe", "hope", "pretty", "guess", "maybe",
    "perhaps", "seems", "appeared to", "tried to"
]

# Resume clichés to avoid
RESUME_CLICHES = [
    "team player",
    "detail-oriented",
    "self-starter",
    "hard worker",
    "results-driven",
    "go-getter",
    "think outside the box",
    "synergy",
    "proactive",
    "go-to person",
    "dynamic",
    "solution-driven",
    "multitasker",
    "excellent communication skills",
    "track record of success",
    "bottom line",
    "value-added",
    "win-win",
    "cutting edge",
    "best of breed",
    "results-oriented",
    "fast-paced environment",
    "think outside the box",
    "synergize",
    "hit the ground running"
]

# List of common action verbs for resumes by category
ACTION_VERBS = {
    "management": [
        "Administered", "Analyzed", "Assigned", "Attained", "Chaired",
        "Consolidated", "Contracted", "Coordinated", "Delegated", "Developed",
        "Directed", "Evaluated", "Executed", "Improved", "Increased",
        "Organized", "Oversaw", "Planned", "Prioritized", "Produced",
        "Recommended", "Reviewed", "Scheduled", "Strengthened", "Supervised"
    ],
    "communication": [
        "Addressed", "Arbitrated", "Arranged", "Authored", "Collaborated",
        "Convinced", "Corresponded", "Developed", "Directed", "Drafted",
        "Edited", "Enlisted", "Formulated", "Influenced", "Interpreted",
        "Lectured", "Mediated", "Moderated", "Negotiated", "Persuaded",
        "Promoted", "Publicized", "Reconciled", "Recruited", "Translated"
    ],
    "research": [
        "Analyzed", "Clarified", "Collected", "Compared", "Conducted",
        "Critiqued", "Detected", "Determined", "Diagnosed", "Evaluated",
        "Examined", "Extracted", "Identified", "Inspected", "Interpreted",
        "Interviewed", "Investigated", "Organized", "Reviewed", "Summarized",
        "Surveyed", "Systematized", "Tested", "Validated", "Verified"
    ],
    "technical": [
        "Assembled", "Built", "Calculated", "Computed", "Designed",
        "Devised", "Engineered", "Fabricated", "Maintained", "Operated",
        "Optimized", "Overhauled", "Programmed", "Redesigned", "Reduced",
        "Remodeled", "Repaired", "Solved", "Standardized", "Upgraded"
    ],
    "teaching": [
        "Adapted", "Advised", "Clarified", "Coached", "Communicated",
        "Coordinated", "Developed", "Enabled", "Encouraged", "Evaluated",
        "Explained", "Facilitated", "Guided", "Informed", "Instructed",
        "Persuaded", "Set goals", "Stimulated", "Taught", "Trained"
    ],
    "creative": [
        "Acted", "Composed", "Conceived", "Conceptualized", "Created",
        "Customized", "Designed", "Developed", "Directed", "Established",
        "Fashioned", "Founded", "Illustrated", "Initiated", "Instituted",
        "Integrated", "Introduced", "Invented", "Originated", "Performed",
        "Planned", "Revitalized", "Shaped", "Visualized"
    ],
    "financial": [
        "Administered", "Allocated", "Analyzed", "Appraised", "Audited",
        "Balanced", "Budgeted", "Calculated", "Computed", "Developed",
        "Forecasted", "Managed", "Marketed", "Planned", "Projected",
        "Researched", "Reduced", "Tracked", "Quantified", "Verified"
    ]
}

def check_spelling(text):
    """
    Check text for spelling errors using a dictionary of common mistakes
    
    Args:
        text: Text to check for spelling errors
    
    Returns:
        tuple: (corrected_text, list of corrections made)
    """
    corrections = []
    corrected_text = text
    
    # Check for each common spelling mistake
    for mistake, correction in COMMON_SPELLING_MISTAKES.items():
        # Create a regex that matches the mistake as a whole word
        pattern = r'\b' + mistake + r'\b'
        if re.search(pattern, corrected_text, re.IGNORECASE):
            # Find all instances of the mistake
            matches = re.finditer(pattern, corrected_text, re.IGNORECASE)
            for match in matches:
                # Get the exact matched text to preserve case
                matched_text = match.group(0)
                if matched_text[0].isupper():
                    replacement = correction.capitalize()
                else:
                    replacement = correction
                
                # Add to list of corrections
                corrections.append((matched_text, replacement))
            
            # Replace all instances of the mistake
            corrected_text = re.sub(pattern, correction, corrected_text, flags=re.IGNORECASE)
    
    return corrected_text, corrections

def check_grammar(text):
    """
    Check text for grammar errors using LanguageTool if available
    
    Args:
        text: Text to check for grammar errors
    
    Returns:
        tuple: (corrected_text, list of corrections or errors)
    """
    if not LANGUAGE_TOOL_AVAILABLE:
        return text, ["Grammar checking requires the language_tool_python package. Install with 'pip install language-tool-python'."]
    
    try:
        # Initialize LanguageTool
        tool = language_tool_python.LanguageTool('en-US')
        
        # Get grammar mistakes
        matches = tool.check(text)
        
        corrections = []
        corrected_text = text
        
        # Apply suggestions
        for match in matches:
            if match.replacements:
                correction = (
                    match.context[match.offset:match.offset + match.errorLength],
                    match.replacements[0]
                )
                corrections.append(correction)
                
                # Replace in text
                corrected_text = corrected_text[:match.offset] + match.replacements[0] + corrected_text[match.offset + match.errorLength:]
        
        tool.close()
        return corrected_text, corrections
    
    except Exception as e:
        return text, [f"Grammar check error: {str(e)}"]

def enhance_text(text):
    """
    Enhance text by replacing weak words with stronger alternatives
    
    Args:
        text: Text to enhance
    
    Returns:
        tuple: (enhanced_text, list of enhancements made)
    """
    enhancements = []
    enhanced_text = text
    
    # Replace weak words
    for weak_word in WEAK_WORDS:
        pattern = r'\b' + weak_word + r'\b'
        if re.search(pattern, enhanced_text, re.IGNORECASE):
            # Just remove the weak word rather than replace it
            enhanced_text = re.sub(pattern, '', enhanced_text, flags=re.IGNORECASE)
            enhancements.append((weak_word, "(removed)"))
    
    # Replace clichés with more specific language
    for cliche in RESUME_CLICHES:
        if cliche in enhanced_text.lower():
            # Suggest removing the cliché
            enhancements.append((cliche, "Consider replacing with more specific achievements"))
    
    # Ensure every bullet point starts with an action verb
    lines = enhanced_text.split('\n')
    for i, line in enumerate(lines):
        # Check if line is a bullet point
        if line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*'):
            content = line.strip()[1:].strip()
            words = content.split()
            
            # If the line has content and doesn't start with an action verb
            if words and not any(verb.lower() == words[0].lower().rstrip(',.:;') for category in ACTION_VERBS.values() for verb in category):
                # Suggest an action verb based on context
                suggested_category = 'management'  # Default category
                
                # Try to determine the most relevant category based on the content
                category_scores = {}
                for category, verbs in ACTION_VERBS.items():
                    score = 0
                    for verb in verbs:
                        if verb.lower() in content.lower():
                            score += 1
                    category_scores[category] = score
                
                if category_scores:
                    suggested_category = max(category_scores.items(), key=lambda x: x[1])[0]
                
                # Suggest a random verb from the category
                suggested_verb = random.choice(ACTION_VERBS[suggested_category])
                
                enhancements.append((f"Bullet point: {content}", f"Consider starting with an action verb like '{suggested_verb}'"))
    
    return enhanced_text, enhancements

def enhance_with_ai(text, job_role):
    """
    Enhance text using Ollama API if available
    
    Args:
        text: Text to enhance
        job_role: Job role for context
    
    Returns:
        tuple: (enhanced_text, explanation)
    """
    try:
        payload = {
            "model": "qwen2.5:3b",
            "prompt": f"""Improve the following resume content for a {job_role} position. 
Make it more impactful, professional, and results-oriented. 
Replace weak phrases with strong action verbs, add metrics where sensible, and ensure it's ATS-friendly.
Do not invent false information. Keep the same general content but improve the phrasing.

CONTENT TO IMPROVE:
{text}

IMPROVED CONTENT:""",
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            enhanced_text = data.get("response", "")
            
            # Generate an explanation of changes
            explanation_prompt = f"""Briefly explain the key improvements made to this resume content:
Original: {text}
Improved: {enhanced_text}

List 3-5 key improvements made:"""
            
            explanation_payload = {
                "model": "qwen2.5:3b",
                "prompt": explanation_prompt,
                "stream": False
            }
            
            explanation_response = requests.post(OLLAMA_API_URL, json=explanation_payload, timeout=10)
            
            if explanation_response.status_code == 200:
                explanation_data = explanation_response.json()
                explanation = explanation_data.get("response", "Text enhanced with stronger language and clarity.")
            else:
                explanation = "Text enhanced with stronger language and clarity."
            
            return enhanced_text, explanation
        
        return text, "Could not connect to Ollama API."
    
    except Exception as e:
        return text, f"Error using AI enhancement: {str(e)}"

def calculate_ats_score(text, job_keywords=None):
    """
    Calculate an ATS compatibility score for resume text
    
    Args:
        text: Resume text
        job_keywords: Optional list of keywords from job description
    
    Returns:
        dict: Score information and suggestions
    """
    score = {
        "overall": 0,
        "keyword_match": 0,
        "format": 0,
        "length": 0,
        "suggestions": []
    }
    
    # Check length (between 400-800 words is ideal)
    words = text.split()
    word_count = len(words)
    
    if word_count < 300:
        score["length"] = 60
        score["suggestions"].append("Resume is too short. Aim for 400-800 words.")
    elif word_count > 1000:
        score["length"] = 70
        score["suggestions"].append("Resume is too long. Aim for 400-800 words.")
    else:
        score["length"] = 100
    
    # Check formatting
    format_score = 100
    
    # Check for common format issues
    if text.count('@') == 0:
        format_score -= 10
        score["suggestions"].append("No email address detected.")
    
    # Check for section headers
    sections = ["experience", "education", "skills", "summary", "objective", "work", "contact"]
    found_sections = 0
    for section in sections:
        if re.search(r'\b' + section + r'\b', text, re.IGNORECASE):
            found_sections += 1
    
    if found_sections < 3:
        format_score -= 20
        score["suggestions"].append("Not enough clear section headers detected. Include clear sections for Experience, Education, Skills, etc.")
    
    # Check for bullet points
    bullets = len(re.findall(r'•|-|\*', text))
    if bullets < 5:
        format_score -= 10
        score["suggestions"].append("Not enough bullet points. Use bullets to highlight achievements and responsibilities.")
    
    score["format"] = max(0, format_score)
    
    # Check keyword match if job keywords provided
    if job_keywords:
        matched_keywords = 0
        for keyword in job_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                matched_keywords += 1
        
        keyword_score = int((matched_keywords / len(job_keywords)) * 100) if job_keywords else 0
        score["keyword_match"] = keyword_score
        
        if keyword_score < 70:
            score["suggestions"].append(f"Low keyword match with job description ({keyword_score}%). Try including more relevant keywords.")
    else:
        score["keyword_match"] = "N/A"
    
    # Calculate overall score
    if score["keyword_match"] != "N/A":
        score["overall"] = int((score["format"] + score["length"] + score["keyword_match"]) / 3)
    else:
        score["overall"] = int((score["format"] + score["length"]) / 2)
    
    # Add general suggestions based on overall score
    if score["overall"] < 70:
        score["suggestions"].append("Overall ATS compatibility is low. Follow the suggestions to improve.")
    elif score["overall"] < 85:
        score["suggestions"].append("Resume has moderate ATS compatibility. Make suggested improvements for better results.")
    else:
        score["suggestions"].append("Resume has good ATS compatibility.")
    
    return score

def extract_keywords_from_job_description(job_description):
    """
    Extract relevant keywords from a job description
    
    Args:
        job_description: Text of the job description
    
    Returns:
        list: Extracted keywords
    """
    try:
        # Try to use Ollama for better extraction
        payload = {
            "model": "qwen2.5:3b",
            "prompt": f"""Extract the most important skills, qualifications, and requirements from this job description. 
Format the result as a simple comma-separated list of keywords with no explanations or commentary.

JOB DESCRIPTION:
{job_description}

KEYWORDS:""",
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            keywords_text = data.get("response", "")
            
            # Parse the comma-separated list
            keywords = [k.strip() for k in keywords_text.split(',')]
            keywords = [k for k in keywords if k]  # Remove empty entries
            
            # Return top 20 keywords
            return keywords[:20]
    except:
        pass
    
    # Fallback to simple extraction
    # Remove common words, focus on nouns, technical terms, etc.
    common_words = set([
        "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be", "been", 
        "being", "in", "on", "at", "by", "for", "with", "about", "against", "between", 
        "into", "through", "during", "before", "after", "above", "below", "to", "from", 
        "up", "down", "of", "off", "over", "under", "again", "further", "then", "once", 
        "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", 
        "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", 
        "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", 
        "don", "should", "now", "you", "we", "our", "company", "position", "job", "role",
        "candidate", "applicant", "ideal", "looking", "must", "required", "preferred",
        "responsibilities", "qualifications", "requirements", "ability", "experience",
        "work", "working", "team", "strong", "excellent", "include", "including"
    ])
    
    # Tokenize and filter
    words = re.findall(r'\b[a-zA-Z][a-zA-Z+#.]*\b', job_description.lower())
    potential_keywords = [word for word in words if word not in common_words and len(word) > 2]
    
    # Count word frequency
    word_counts = {}
    for word in potential_keywords:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    
    # Extract multiword terms (e.g., "machine learning")
    word_pairs = []
    words = job_description.lower().split()
    for i in range(len(words) - 1):
        if words[i] not in common_words and words[i+1] not in common_words:
            word_pair = f"{words[i]} {words[i+1]}"
            word_pairs.append(word_pair)
    
    # Count pair frequency
    for pair in word_pairs:
        if pair in word_counts:
            word_counts[pair] += 3  # Give higher weight to multi-word terms
        else:
            word_counts[pair] = 3
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [keyword for keyword, count in sorted_keywords[:20]] 