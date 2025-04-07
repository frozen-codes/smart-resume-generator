"""
Resume Templates Module for Resume Generator
Provides different templates for formatting resumes
"""

# Modern template with clean markdown formatting
MODERN_TEMPLATE = """
# {name}
**{job_role}** | {email} | {phone} | {location}

## SUMMARY
{summary}

## SKILLS
{skills}

## EXPERIENCE
{experience}

## EDUCATION
{education}

## CONTACT
Email: {email}
Phone: {phone}
Location: {location}
{links}
"""

# Classic template with traditional formatting
CLASSIC_TEMPLATE = """
{name}
====================
{job_role}
Contact: {email} | {phone} | {location}

SUMMARY
--------------------
{summary}

SKILLS
--------------------
{skills}

EXPERIENCE
--------------------
{experience}

EDUCATION
--------------------
{education}

CONTACT INFORMATION
--------------------
Email: {email}
Phone: {phone}
Address: {location}
{links}
"""

# Minimalist template with streamlined formatting
MINIMALIST_TEMPLATE = """
# {name}
{job_role} | {location}

**About Me**
{summary}

**Skills**
{skills}

**Experience**
{experience}

**Education**
{education}

**Contact**
{email} | {phone}
{links}
"""

# Dark template with special formatting for dark mode
DARK_TEMPLATE = """
# {name}
## {job_role}
*{location}*

### PROFESSIONAL SUMMARY
{summary}

### TECHNICAL SKILLS
{skills}

### PROFESSIONAL EXPERIENCE
{experience}

### EDUCATION
{education}

### CONTACT INFORMATION
- Email: {email}
- Phone: {phone}
- Location: {location}
{links}
"""

def get_template(template_name="modern", dark_mode=False):
    """
    Get the specified template
    
    Args:
        template_name: Name of the template to use
        dark_mode: Whether to use dark mode
        
    Returns:
        str: Template string
    """
    if dark_mode and template_name.lower() != "dark":
        # Use dark template if dark mode is enabled
        return DARK_TEMPLATE
    
    templates = {
        "modern": MODERN_TEMPLATE,
        "classic": CLASSIC_TEMPLATE,
        "minimalist": MINIMALIST_TEMPLATE,
        "dark": DARK_TEMPLATE
    }
    
    return templates.get(template_name.lower(), MODERN_TEMPLATE)

def format_resume(template_name, **kwargs):
    """
    Format a resume using the specified template
    
    Args:
        template_name: Name of the template to use
        **kwargs: Keyword arguments to fill template
        
    Returns:
        str: Formatted resume text
    """
    dark_mode = kwargs.pop('dark_mode', False)
    template = get_template(template_name, dark_mode)
    
    # Ensure all required fields are available
    defaults = {
        'name': '',
        'job_role': '',
        'summary': '',
        'skills': '',
        'experience': '',
        'education': '',
        'email': '',
        'phone': '',
        'location': '',
        'links': ''
    }
    
    # Update defaults with provided values
    for key, value in kwargs.items():
        if key in defaults:
            defaults[key] = value
    
    # Format skills as bullet points if they're comma-separated
    if ',' in defaults['skills']:
        skills_list = [skill.strip() for skill in defaults['skills'].split(',')]
        formatted_skills = '\n'.join([f"- {skill}" for skill in skills_list])
        defaults['skills'] = formatted_skills
    
    # Format the resume
    return template.format(**defaults) 