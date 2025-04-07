#!/usr/bin/env python3
"""
Enhanced Resume Generator
A comprehensive application for creating professional resumes with multiple templates,
AI-powered suggestions, and advanced formatting options.
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import datetime
import socket
import re
import random
import webbrowser
from tkinter import font as tkfont

# Try to import optional modules
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Ollama API settings
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

# Path for resume history
HISTORY_FILE = "resume_history.json"

# Try to import our custom modules with graceful fallbacks
try:
    import resume_templates
    TEMPLATES_AVAILABLE = True
except ImportError:
    TEMPLATES_AVAILABLE = False
    print("Warning: resume_templates module not found. Basic templates will be used.")

try:
    import resume_export
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False
    print("Warning: resume_export module not found. Export functionality will be limited.")

try:
    import ai_suggestions
    AI_SUGGESTIONS_AVAILABLE = True
except ImportError:
    AI_SUGGESTIONS_AVAILABLE = False
    print("Warning: ai_suggestions module not found. AI suggestions will not be available.")

try:
    import text_enhancer
    TEXT_ENHANCER_AVAILABLE = True
except ImportError:
    TEXT_ENHANCER_AVAILABLE = False
    print("Warning: text_enhancer module not found. Text enhancement will not be available.")

try:
    import qr_generator
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("Warning: qr_generator module not found. QR code generation will not be available.")

try:
    import linkedin_import
    LINKEDIN_IMPORT_AVAILABLE = True
except ImportError:
    LINKEDIN_IMPORT_AVAILABLE = False
    print("Warning: linkedin_import module not found. LinkedIn import will not be available.")

# Define basic templates in case resume_templates module is not available
BASIC_TEMPLATES = {
    "modern": """
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
""",
    "classic": """
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
}

class ModernWidget:
    """Helper class to apply modern styling to tkinter widgets"""
    @staticmethod
    def style_frame(frame, bg="#f0f0f0", relief=tk.FLAT):
        frame.configure(bg=bg, relief=relief)
        return frame
    
    @staticmethod
    def style_label(label, bg="#f0f0f0", fg="#333333", font=("Helvetica", 10)):
        label.configure(bg=bg, fg=fg, font=font)
        return label
    
    @staticmethod
    def style_entry(entry, bg="#ffffff", fg="#333333", font=("Helvetica", 10)):
        entry.configure(bg=bg, fg=fg, font=font, relief=tk.SOLID, bd=1)
        return entry
    
    @staticmethod
    def style_button(button, bg="#4a6fa5", fg="#ffffff", font=("Helvetica", 10, "bold"),
                    activebackground="#3b5998", activeforeground="#ffffff"):
        button.configure(bg=bg, fg=fg, font=font, 
                         activebackground=activebackground, 
                         activeforeground=activeforeground,
                         relief=tk.RAISED, bd=1, padx=10, pady=5)
        return button
    
    @staticmethod
    def style_text(text, bg="#ffffff", fg="#333333", font=("Helvetica", 10)):
        text.configure(bg=bg, fg=fg, font=font, relief=tk.SOLID, bd=1)
        return text

def check_ollama_connection():
    """Check if Ollama API is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 11434))
        sock.close()
        return result == 0
    except:
        return False

def generate_resume_with_ai(name, job_role, skills, experience, education, email, phone, location, links=""):
    """Generate a resume using the Ollama API"""
    if not REQUESTS_AVAILABLE:
        raise ImportError("The requests module is required for AI generation")
        
    try:
        # Check if Ollama is available
        if not check_ollama_connection():
            raise ConnectionError("Could not connect to Ollama API")
        
        # Prepare the prompt for Ollama
        prompt = f"""Create a professional resume for the following individual:

Name: {name}
Job Role: {job_role}
Skills: {skills}
Experience: {experience}
Education: {education}
Email: {email}
Phone: {phone}
Location: {location}
Links: {links}

Format the resume with markdown, using sections for Summary, Skills, Experience, Education, and Contact Information.
Be concise, professional, and highlight key achievements. Write in third person.
"""
        
        # Create the payload for the API
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        # Send the request to Ollama
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            generated_resume = result.get("response", "")
            
            if not generated_resume:
                raise ValueError("Received empty response from Ollama")
            
            return generated_resume
        else:
            raise ConnectionError(f"Error connecting to Ollama API: {response.status_code}")
            
    except Exception as e:
        # Fall back to template-based resume formatting
        print(f"Error generating resume with AI: {str(e)}")
        return format_resume_from_template(name, job_role, skills, experience, education, email, phone, location, links)

def format_resume_from_template(name, job_role, skills, experience, education, email, phone, location, links="", template_name="modern"):
    """Format resume using templates when AI generation is unavailable"""
    # Use imported templates if available, otherwise use basic templates
    if TEMPLATES_AVAILABLE:
        return resume_templates.format_resume(
            template_name,
            name=name,
            job_role=job_role,
            summary=get_summary(job_role),
            skills=skills,
            experience=experience,
            education=education,
            email=email,
            phone=phone,
            location=location,
            links=links
        )
    else:
        # Use basic templates
        template = BASIC_TEMPLATES.get(template_name.lower(), BASIC_TEMPLATES["modern"])
        
        return template.format(
            name=name,
            job_role=job_role,
            summary=get_summary(job_role),
            skills=skills,
            experience=experience,
            education=education,
            email=email,
            phone=phone,
            location=location,
            links=links
        )

def get_summary(job_role):
    """Generate a summary based on job role"""
    if AI_SUGGESTIONS_AVAILABLE:
        return ai_suggestions.get_summary_suggestion(job_role)
    
    # Default summary if AI suggestions not available
    return f"Experienced {job_role} with a proven track record of delivering high-quality results."

def save_resume_as_text(resume_text, filename="resume.txt"):
    """Save resume as text file"""
    if EXPORT_AVAILABLE:
        return resume_export.save_as_text(resume_text, filename)
    else:
        # Fallback if export module not available
        with open(filename, "w", encoding="utf-8") as f:
            f.write(resume_text)
        return os.path.abspath(filename)

def export_resume(resume_text, format_type="txt", filename=None):
    """Export resume in different formats"""
    if not EXPORT_AVAILABLE:
        return save_resume_as_text(resume_text)
    
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{timestamp}"
    
    if format_type == "txt":
        return resume_export.save_as_text(resume_text, f"{filename}.txt")
    elif format_type == "html":
        return resume_export.save_as_html(resume_text, f"{filename}.html")
    elif format_type == "docx" and hasattr(resume_export, 'save_as_docx'):
        return resume_export.save_as_docx(resume_text, f"{filename}.docx")
    elif format_type == "pdf" and hasattr(resume_export, 'save_as_pdf'):
        return resume_export.save_as_pdf(resume_text, f"{filename}.pdf")
    else:
        # Default to text format
        return save_resume_as_text(resume_text, f"{filename}.txt")

def save_resume_to_history(resume_data):
    """Save resume to history file"""
    history = []
    
    # Load existing history if available
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            pass
    
    # Add timestamp
    resume_data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add to history
    history.append(resume_data)
    
    # Save history
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

class ResumeGeneratorApp:
    """Main application class for the Resume Generator"""
    
    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.root.title("Enhanced Resume Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Variables
        self.name_var = tk.StringVar()
        self.job_role_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.linkedin_var = tk.StringVar()
        self.website_var = tk.StringVar()
        self.template_var = tk.StringVar(value="modern")
        self.export_format_var = tk.StringVar(value="txt")
        self.dark_mode_var = tk.BooleanVar(value=False)
        self.qr_var = tk.BooleanVar(value=False)
        
        # Resume text
        self.resume_text = ""
        
        # Create UI
        self.create_ui()
        
        # Check Ollama connection
        self.check_ollama_status()
    
    def create_ui(self):
        """Create the user interface"""
        # Create main frames
        self.create_header_frame()
        self.create_main_frame()
        self.create_footer_frame()
    
    def check_ollama_status(self):
        """Check Ollama connection status"""
        if check_ollama_connection():
            self.connection_label.config(text="API is accessible")
        else:
            self.connection_label.config(text="API is not accessible")

    def create_header_frame(self):
        """Create the header frame with app title and status"""
        header_frame = tk.Frame(self.root, bg="#4a6fa5", height=60)
        header_frame.pack(fill=tk.X)
        
        # App title
        title_label = tk.Label(header_frame, text="Enhanced Resume Generator", 
                              font=("Helvetica", 16, "bold"), bg="#4a6fa5", fg="white")
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Connection status
        self.connection_label = tk.Label(header_frame, text="Checking API...", 
                                       font=("Helvetica", 10), bg="#4a6fa5", fg="white")
        self.connection_label.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def create_main_frame(self):
        """Create the main content frame with input form and preview"""
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create left panel (input form)
        self.create_input_panel(main_frame)
        
        # Create right panel (preview)
        self.create_preview_panel(main_frame)
    
    def create_input_panel(self, parent):
        """Create the input form panel"""
        form_frame = tk.Frame(parent, bg="#f0f0f0", width=500)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # Add tabs
        tab_control = ttk.Notebook(form_frame)
        
        # Personal info tab
        personal_tab = tk.Frame(tab_control, bg="#f0f0f0")
        self.create_personal_info_form(personal_tab)
        tab_control.add(personal_tab, text="Personal Info")
        
        # Experience tab
        experience_tab = tk.Frame(tab_control, bg="#f0f0f0")
        self.create_experience_form(experience_tab)
        tab_control.add(experience_tab, text="Experience")
        
        # Education tab
        education_tab = tk.Frame(tab_control, bg="#f0f0f0")
        self.create_education_form(education_tab)
        tab_control.add(education_tab, text="Education")
        
        # Skills tab
        skills_tab = tk.Frame(tab_control, bg="#f0f0f0")
        self.create_skills_form(skills_tab)
        tab_control.add(skills_tab, text="Skills")
        
        # Template tab
        template_tab = tk.Frame(tab_control, bg="#f0f0f0")
        self.create_template_form(template_tab)
        tab_control.add(template_tab, text="Template")
        
        # LinkedIn Import tab (if available)
        if LINKEDIN_IMPORT_AVAILABLE:
            linkedin_tab = tk.Frame(tab_control, bg="#f0f0f0")
            self.create_linkedin_form(linkedin_tab)
            tab_control.add(linkedin_tab, text="Import")
        
        tab_control.pack(expand=True, fill=tk.BOTH)
        
        # Generate button
        generate_frame = tk.Frame(form_frame, bg="#f0f0f0", pady=10)
        generate_frame.pack(fill=tk.X)
        
        generate_button = tk.Button(generate_frame, text="Generate Resume", 
                                  command=self.generate_resume)
        ModernWidget.style_button(generate_button, bg="#28a745", activebackground="#218838")
        generate_button.pack(fill=tk.X, padx=20)
    
    def create_personal_info_form(self, parent):
        """Create the personal information form"""
        # Create a canvas with scrollbar
        canvas = tk.Canvas(parent, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        fields = [
            ("Full Name", self.name_var),
            ("Job Role", self.job_role_var),
            ("Email", self.email_var),
            ("Phone", self.phone_var),
            ("Location", self.location_var),
            ("LinkedIn URL", self.linkedin_var),
            ("Website URL", self.website_var)
        ]
        
        for i, (label_text, var) in enumerate(fields):
            frame = tk.Frame(scroll_frame, bg="#f0f0f0", pady=5)
            frame.pack(fill=tk.X, padx=10)
            
            label = tk.Label(frame, text=label_text, width=15, anchor="w")
            ModernWidget.style_label(label)
            label.pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, textvariable=var, width=30)
            ModernWidget.style_entry(entry)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_experience_form(self, parent):
        """Create the experience form"""
        # Create a canvas with scrollbar
        canvas = tk.Canvas(parent, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Instructions
        instructions = tk.Label(scroll_frame, text="Enter your work experience (most recent first)",
                              font=("Helvetica", 10, "bold"), bg="#f0f0f0")
        instructions.pack(pady=10)
        
        # Experience text area
        experience_label = tk.Label(scroll_frame, text="Experience (Markdown format):", anchor="w")
        ModernWidget.style_label(experience_label)
        experience_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.experience_text = scrolledtext.ScrolledText(scroll_frame, height=15)
        ModernWidget.style_text(self.experience_text)
        self.experience_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.experience_text.insert(tk.END, """### Job Title
**Company Name** | 2020 - Present

- Accomplishment 1
- Accomplishment 2
- Accomplishment 3

### Previous Job Title
**Previous Company** | 2015 - 2020

- Accomplishment 1
- Accomplishment 2""")
        
        # AI Suggestions button (if available)
        if AI_SUGGESTIONS_AVAILABLE:
            suggestion_frame = tk.Frame(scroll_frame, bg="#f0f0f0", pady=5)
            suggestion_frame.pack(fill=tk.X, padx=10)
            
            suggest_button = tk.Button(suggestion_frame, text="Get Suggestions", 
                                    command=self.get_experience_suggestions)
            ModernWidget.style_button(suggest_button, bg="#6c757d", activebackground="#5a6268")
            suggest_button.pack(side=tk.LEFT)
    
    def create_education_form(self, parent):
        """Create the education form"""
        # Create a canvas with scrollbar
        canvas = tk.Canvas(parent, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Instructions
        instructions = tk.Label(scroll_frame, text="Enter your education (most recent first)",
                              font=("Helvetica", 10, "bold"), bg="#f0f0f0")
        instructions.pack(pady=10)
        
        # Education text area
        education_label = tk.Label(scroll_frame, text="Education (Markdown format):", anchor="w")
        ModernWidget.style_label(education_label)
        education_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.education_text = scrolledtext.ScrolledText(scroll_frame, height=10)
        ModernWidget.style_text(self.education_text)
        self.education_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.education_text.insert(tk.END, """### Bachelor of Science in Computer Science
**University Name** | 2015 - 2019

### High School Diploma
**School Name** | 2011 - 2015""")
    
    def create_skills_form(self, parent):
        """Create the skills form"""
        # Create a canvas with scrollbar
        canvas = tk.Canvas(parent, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Instructions
        instructions = tk.Label(scroll_frame, text="Enter your skills (comma separated)",
                              font=("Helvetica", 10, "bold"), bg="#f0f0f0")
        instructions.pack(pady=10)
        
        # Skills text area
        skills_label = tk.Label(scroll_frame, text="Skills:", anchor="w")
        ModernWidget.style_label(skills_label)
        skills_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.skills_text = scrolledtext.ScrolledText(scroll_frame, height=10)
        ModernWidget.style_text(self.skills_text)
        self.skills_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.skills_text.insert(tk.END, "Python, JavaScript, HTML/CSS, SQL, Git, React, Docker, AWS, Project Management, Communication")
        
        # AI Suggestions button (if available)
        if AI_SUGGESTIONS_AVAILABLE:
            suggestion_frame = tk.Frame(scroll_frame, bg="#f0f0f0", pady=5)
            suggestion_frame.pack(fill=tk.X, padx=10)
            
            suggest_button = tk.Button(suggestion_frame, text="Suggest Skills", 
                                    command=self.get_skills_suggestions)
            ModernWidget.style_button(suggest_button, bg="#6c757d", activebackground="#5a6268")
            suggest_button.pack(side=tk.LEFT)
    
    def create_template_form(self, parent):
        """Create the template selection form"""
        # Create a canvas with scrollbar
        canvas = tk.Canvas(parent, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Template selection
        template_label = tk.Label(scroll_frame, text="Select Template:", 
                                font=("Helvetica", 10, "bold"), bg="#f0f0f0")
        template_label.pack(pady=(10, 5))
        
        # Get available templates
        if TEMPLATES_AVAILABLE:
            templates = ["modern", "classic", "minimalist", "dark"]
        else:
            templates = ["modern", "classic"]
        
        for template in templates:
            rb = tk.Radiobutton(scroll_frame, text=template.capitalize(), 
                                value=template, variable=self.template_var)
            rb.configure(bg="#f0f0f0", activebackground="#f0f0f0")
            rb.pack(anchor="w", padx=20, pady=5)
        
        # Export format
        export_label = tk.Label(scroll_frame, text="Export Format:", 
                              font=("Helvetica", 10, "bold"), bg="#f0f0f0")
        export_label.pack(pady=(20, 5))
        
        # Available export formats
        if EXPORT_AVAILABLE:
            export_formats = ["txt", "html", "docx", "pdf"]
        else:
            export_formats = ["txt"]
        
        for format_type in export_formats:
            rb = tk.Radiobutton(scroll_frame, text=format_type.upper(), 
                                value=format_type, variable=self.export_format_var)
            rb.configure(bg="#f0f0f0", activebackground="#f0f0f0")
            rb.pack(anchor="w", padx=20, pady=5)
        
        # Dark mode option
        if "dark" in templates:
            dark_check = tk.Checkbutton(scroll_frame, text="Dark Mode", 
                                     variable=self.dark_mode_var)
            dark_check.configure(bg="#f0f0f0", activebackground="#f0f0f0")
            dark_check.pack(anchor="w", padx=20, pady=20)
        
        # QR Code option
        if QR_AVAILABLE:
            qr_check = tk.Checkbutton(scroll_frame, text="Add QR Code", 
                                    variable=self.qr_var)
            qr_check.configure(bg="#f0f0f0", activebackground="#f0f0f0")
            qr_check.pack(anchor="w", padx=20, pady=5)
    
    def create_preview_panel(self, parent):
        """Create the resume preview panel"""
        preview_frame = tk.LabelFrame(parent, text="Resume Preview", bg="#f0f0f0")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Preview area
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD)
        ModernWidget.style_text(self.preview_text)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Set initial content
        self.preview_text.insert(tk.END, "Your resume preview will appear here...")
        
        # Export button
        export_button = tk.Button(preview_frame, text="Export Resume", 
                                command=self.export_current_resume)
        ModernWidget.style_button(export_button, bg="#007bff", activebackground="#0069d9")
        export_button.pack(pady=10)
        
        # Enhancement options (if available)
        if TEXT_ENHANCER_AVAILABLE:
            enhance_frame = tk.Frame(preview_frame, bg="#f0f0f0")
            enhance_frame.pack(fill=tk.X, pady=10)
            
            spell_check_button = tk.Button(enhance_frame, text="Spell Check", 
                                        command=self.check_spelling)
            ModernWidget.style_button(spell_check_button, bg="#6c757d", activebackground="#5a6268")
            spell_check_button.pack(side=tk.LEFT, padx=5)
            
            enhance_button = tk.Button(enhance_frame, text="Enhance Text", 
                                    command=self.enhance_resume)
            ModernWidget.style_button(enhance_button, bg="#6c757d", activebackground="#5a6268")
            enhance_button.pack(side=tk.LEFT, padx=5)
            
            self.ats_score_var = tk.StringVar(value="ATS Score: Not calculated")
            ats_label = tk.Label(enhance_frame, textvariable=self.ats_score_var, bg="#f0f0f0")
            ats_label.pack(side=tk.RIGHT, padx=5)
    
    def create_footer_frame(self):
        """Create the footer frame with status and buttons"""
        footer_frame = tk.Frame(self.root, bg="#f0f0f0", height=40)
        footer_frame.pack(fill=tk.X, pady=5)
        
        # Status message
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(footer_frame, textvariable=self.status_var, bg="#f0f0f0")
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Help button
        help_button = tk.Button(footer_frame, text="Help", command=self.show_help)
        help_button.configure(bg="#f0f0f0", relief=tk.FLAT)
        help_button.pack(side=tk.RIGHT, padx=10)

    def create_linkedin_form(self, parent):
        """Create LinkedIn import form"""
        frame = tk.Frame(parent, bg="#f0f0f0", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = tk.Label(frame, text="Import data from LinkedIn export file", 
                              font=("Helvetica", 10, "bold"), bg="#f0f0f0")
        instructions.pack(pady=10)
        
        desc = tk.Label(frame, text="Select a LinkedIn data export file (JSON or CSV)", 
                      bg="#f0f0f0", wraplength=400)
        desc.pack(pady=(0, 10))
        
        # File selection
        file_frame = tk.Frame(frame, bg="#f0f0f0")
        file_frame.pack(fill=tk.X, pady=10)
        
        self.linkedin_file_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.linkedin_file_var, width=30)
        ModernWidget.style_entry(file_entry)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = tk.Button(file_frame, text="Browse", command=self.browse_linkedin_file)
        ModernWidget.style_button(browse_button)
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Import button
        import_button = tk.Button(frame, text="Import LinkedIn Data", 
                                command=self.import_linkedin_data)
        ModernWidget.style_button(import_button, bg="#5bc0de", activebackground="#31b0d5")
        import_button.pack(pady=20)
        
        # Status
        self.linkedin_status = tk.Label(frame, text="", bg="#f0f0f0", wraplength=400)
        self.linkedin_status.pack(pady=10)
    
    def browse_linkedin_file(self):
        """Browse for a LinkedIn export file"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("LinkedIn Export Files", "*.json;*.csv"),
                ("JSON Files", "*.json"),
                ("CSV Files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.linkedin_file_var.set(filename)
    
    def import_linkedin_data(self):
        """Import data from LinkedIn export file"""
        if not LINKEDIN_IMPORT_AVAILABLE:
            messagebox.showinfo("Import", "LinkedIn import module not available")
            return
        
        file_path = self.linkedin_file_var.get().strip()
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Import Error", "Select a valid LinkedIn export file")
            return
        
        try:
            # Update status
            self.linkedin_status.config(text="Importing data...")
            self.root.update_idletasks()
            
            # Determine file type and parse
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.json':
                profile_data = linkedin_import.parse_linkedin_json(file_path)
            elif file_extension == '.csv':
                profile_data = linkedin_import.parse_linkedin_csv(file_path)
            else:
                raise ValueError("Unsupported file format. Use JSON or CSV LinkedIn export files.")
            
            # Populate form fields with imported data
            if profile_data.get('name'):
                self.name_var.set(profile_data['name'])
            
            if profile_data.get('job_role'):
                self.job_role_var.set(profile_data['job_role'])
            
            if profile_data.get('contact_info', {}).get('email'):
                self.email_var.set(profile_data['contact_info']['email'])
            
            if profile_data.get('location'):
                self.location_var.set(profile_data['location'])
            
            if profile_data.get('skills'):
                self.skills_text.delete("1.0", tk.END)
                self.skills_text.insert(tk.END, ", ".join(profile_data['skills']))
            
            if profile_data.get('experience'):
                # Format experience for the form
                experience_text = linkedin_import.format_experience_for_resume(profile_data['experience'])
                self.experience_text.delete("1.0", tk.END)
                self.experience_text.insert(tk.END, experience_text)
            
            if profile_data.get('education'):
                # Format education for the form
                education_text = linkedin_import.format_education_for_resume(profile_data['education'])
                self.education_text.delete("1.0", tk.END)
                self.education_text.insert(tk.END, education_text)
            
            # Update status
            self.linkedin_status.config(
                text=f"Data imported successfully from {os.path.basename(file_path)}"
            )
        
        except Exception as e:
            self.linkedin_status.config(text=f"Import error: {str(e)}")
            messagebox.showerror("Import Error", str(e))
    
    def get_skills_suggestions(self):
        """Get AI-powered skill suggestions"""
        if not AI_SUGGESTIONS_AVAILABLE:
            messagebox.showinfo("Suggestions", "AI suggestions module not available")
            return
        
        job_role = self.job_role_var.get().strip()
        
        if not job_role:
            messagebox.showinfo("Suggestions", "Enter a job role first")
            return
        
        try:
            # Update status
            self.status_var.set("Getting skills suggestions...")
            self.root.update_idletasks()
            
            # Get suggestions
            suggestions = ai_suggestions.get_skill_suggestions(job_role)
            
            if not suggestions:
                messagebox.showinfo("Suggestions", "No suggestions available for this job role")
                return
            
            # Format suggestions
            suggested_skills = ", ".join(suggestions)
            
            # Ask if user wants to use suggestions
            if messagebox.askyesno("Skills Suggestions", 
                                  f"Suggested skills for {job_role}:\n\n{suggested_skills}\n\nUse these suggestions?"):
                
                # Replace skills
                self.skills_text.delete("1.0", tk.END)
                self.skills_text.insert(tk.END, suggested_skills)
            
            # Update status
            self.status_var.set("Skills suggestions retrieved")
        
        except Exception as e:
            self.status_var.set(f"Suggestion error: {str(e)}")
            messagebox.showerror("Suggestion Error", str(e))
    
    def get_experience_suggestions(self):
        """Get AI-powered experience suggestions"""
        if not AI_SUGGESTIONS_AVAILABLE:
            messagebox.showinfo("Suggestions", "AI suggestions module not available")
            return
        
        job_role = self.job_role_var.get().strip()
        
        if not job_role:
            messagebox.showinfo("Suggestions", "Enter a job role first")
            return
        
        try:
            # Create a dialog to get position title
            position_dialog = tk.Toplevel(self.root)
            position_dialog.title("Experience Suggestions")
            position_dialog.geometry("400x200")
            position_dialog.configure(bg="#f0f0f0")
            position_dialog.grab_set()  # Make dialog modal
            
            # Position title entry
            frame = tk.Frame(position_dialog, bg="#f0f0f0", pady=10)
            frame.pack(fill=tk.X, padx=10)
            
            label = tk.Label(frame, text="Position Title:", width=15, anchor="w")
            ModernWidget.style_label(label)
            label.pack(side=tk.LEFT)
            
            position_var = tk.StringVar()
            entry = tk.Entry(frame, textvariable=position_var, width=30)
            ModernWidget.style_entry(entry)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Suggestion result area
            result_label = tk.Label(position_dialog, text="Suggestion will appear here:", 
                                   anchor="w", bg="#f0f0f0")
            result_label.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            result_text = scrolledtext.ScrolledText(position_dialog, height=5)
            ModernWidget.style_text(result_text)
            result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Get suggestion button
            def get_position_suggestion():
                position = position_var.get().strip()
                
                if not position:
                    messagebox.showinfo("Suggestions", "Enter a position title")
                    return
                
                try:
                    # Get suggestion
                    bullet_points = ai_suggestions.get_experience_bullet_points(job_role, position, 3)
                    
                    # Display suggestion
                    result_text.delete("1.0", tk.END)
                    result_text.insert(tk.END, "\n".join([f"- {point}" for point in bullet_points]))
                
                except Exception as e:
                    messagebox.showerror("Suggestion Error", str(e))
            
            # Action buttons
            button_frame = tk.Frame(position_dialog, bg="#f0f0f0", pady=10)
            button_frame.pack(fill=tk.X, padx=10)
            
            get_button = tk.Button(button_frame, text="Get Suggestion", command=get_position_suggestion)
            ModernWidget.style_button(get_button)
            get_button.pack(side=tk.LEFT, padx=5)
            
            def use_suggestion():
                suggestion = result_text.get("1.0", tk.END).strip()
                
                if not suggestion:
                    return
                
                # Get current experience text
                current_text = self.experience_text.get("1.0", tk.END)
                
                # Add suggestion as a bullet point to the first job
                import re
                sections = re.split(r'(###.*)', current_text)
                
                if len(sections) >= 3:  # Has at least one job section
                    # Add to the first job section
                    sections[2] = sections[2].rstrip() + f"\n{suggestion}\n"
                    
                    # Update experience text
                    new_text = "".join(sections)
                    self.experience_text.delete("1.0", tk.END)
                    self.experience_text.insert(tk.END, new_text)
                else:
                    # Just append to current text
                    self.experience_text.insert(tk.END, f"\n{suggestion}")
                
                # Close dialog
                position_dialog.destroy()
            
            use_button = tk.Button(button_frame, text="Use Suggestion", command=use_suggestion)
            ModernWidget.style_button(use_button, bg="#28a745", activebackground="#218838")
            use_button.pack(side=tk.LEFT, padx=5)
            
            cancel_button = tk.Button(button_frame, text="Cancel", 
                                   command=position_dialog.destroy)
            ModernWidget.style_button(cancel_button, bg="#dc3545", activebackground="#c82333")
            cancel_button.pack(side=tk.RIGHT, padx=5)
        
        except Exception as e:
            self.status_var.set(f"Suggestion error: {str(e)}")
            messagebox.showerror("Suggestion Error", str(e))
    
    def show_help(self):
        """Show help information"""
        help_text = """
Enhanced Resume Generator Help

This application helps you create professional resumes with different templates and features.

Features:
- Multiple resume templates
- AI-powered content generation
- Export in various formats (TXT, HTML, DOCX, PDF)
- LinkedIn data import
- Spell checking and text enhancement
- ATS score calculation
- QR code generation

Tips:
- Fill in all personal information for a complete resume
- Use the markdown format for experience and education
- Try different templates to find the best fit
- Use the AI suggestions to improve your content
- Check your ATS score to optimize for job applications
- Add a QR code linking to your LinkedIn profile

For more information, visit the help documentation.
"""
        
        # Create help window
        help_window = tk.Toplevel(self.root)
        help_window.title("Resume Generator Help")
        help_window.geometry("600x400")
        help_window.configure(bg="#f0f0f0")
        
        # Help text area
        help_text_area = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        ModernWidget.style_text(help_text_area)
        help_text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert help text
        help_text_area.insert(tk.END, help_text)
        
        # Close button
        close_button = tk.Button(help_window, text="Close", command=help_window.destroy)
        ModernWidget.style_button(close_button)
        close_button.pack(pady=10)

    def generate_resume(self):
        """Generate a resume based on the form data"""
        try:
            # Get form data
            name = self.name_var.get().strip()
            job_role = self.job_role_var.get().strip()
            email = self.email_var.get().strip()
            phone = self.phone_var.get().strip()
            location = self.location_var.get().strip()
            
            # Validate required fields
            if not name or not job_role:
                messagebox.showerror("Error", "Name and Job Role are required fields")
                return
            
            # Get skills, experience, and education
            skills = self.skills_text.get("1.0", tk.END).strip()
            experience = self.experience_text.get("1.0", tk.END).strip()
            education = self.education_text.get("1.0", tk.END).strip()
            
            # Get links
            links = ""
            if self.linkedin_var.get().strip():
                links += f"LinkedIn: {self.linkedin_var.get().strip()}\n"
            if self.website_var.get().strip():
                links += f"Website: {self.website_var.get().strip()}\n"
            
            # Update status
            self.status_var.set("Generating resume...")
            self.root.update_idletasks()
            
            # Try to generate with AI first
            try:
                if check_ollama_connection() and REQUESTS_AVAILABLE:
                    self.resume_text = generate_resume_with_ai(
                        name, job_role, skills, experience, education, 
                        email, phone, location, links
                    )
                else:
                    # Fall back to template
                    template_name = self.template_var.get()
                    self.resume_text = format_resume_from_template(
                        name, job_role, skills, experience, education,
                        email, phone, location, links, template_name
                    )
            except Exception as e:
                # Fall back to template on error
                template_name = self.template_var.get()
                self.resume_text = format_resume_from_template(
                    name, job_role, skills, experience, education,
                    email, phone, location, links, template_name
                )
            
            # Update preview
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, self.resume_text)
            
            # Generate QR code if requested
            if self.qr_var.get() and QR_AVAILABLE:
                self.generate_qr_code()
            
            # Save to history
            resume_data = {
                "name": name,
                "job_role": job_role,
                "skills": skills,
                "experience": experience,
                "education": education,
                "email": email,
                "phone": phone,
                "location": location,
                "links": links,
                "template": self.template_var.get(),
                "resume_text": self.resume_text
            }
            save_resume_to_history(resume_data)
            
            # Calculate ATS score if enhancer is available
            if TEXT_ENHANCER_AVAILABLE:
                self.calculate_ats_score()
            
            # Update status
            self.status_var.set("Resume generated successfully")
        
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate resume: {str(e)}")
    
    def generate_qr_code(self):
        """Generate QR code for LinkedIn or website URL"""
        if not QR_AVAILABLE:
            return
        
        try:
            # Choose URL to use (LinkedIn preferred)
            url = self.linkedin_var.get().strip()
            if not url:
                url = self.website_var.get().strip()
            
            if not url:
                return
            
            # Generate QR code
            name = self.name_var.get().strip()
            
            if name and "linkedin.com" in url.lower():
                # Use LinkedIn themed QR code if it's a LinkedIn URL
                qr_file = qr_generator.generate_qr_with_linkedin_template(
                    url, name
                )
            else:
                # Use standard QR code
                qr_file = qr_generator.generate_qr_code(url)
            
            # Show message with QR code path
            if not qr_file.startswith("Error"):
                messagebox.showinfo("QR Code", f"QR code generated successfully: {qr_file}")
        
        except Exception as e:
            messagebox.showerror("QR Code Error", str(e))
    
    def export_current_resume(self):
        """Export the current resume"""
        if not self.resume_text:
            messagebox.showinfo("Export", "Generate a resume first")
            return
        
        try:
            # Get export format
            format_type = self.export_format_var.get()
            
            # Ask for save location
            file_types = {
                "txt": [("Text files", "*.txt"), ("All files", "*.*")],
                "html": [("HTML files", "*.html"), ("All files", "*.*")],
                "docx": [("Word documents", "*.docx"), ("All files", "*.*")],
                "pdf": [("PDF files", "*.pdf"), ("All files", "*.*")]
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=file_types.get(format_type, [("All files", "*.*")])
            )
            
            if not filename:
                return
            
            # Export resume
            dark_mode = self.dark_mode_var.get()
            
            if format_type == "html" and EXPORT_AVAILABLE:
                result = resume_export.save_as_html(self.resume_text, filename, dark_mode)
            else:
                result = export_resume(self.resume_text, format_type, filename)
            
            # Show success message
            if not result.startswith("Error"):
                self.status_var.set(f"Resume exported as {format_type.upper()}")
                
                # Ask if user wants to open the file
                if messagebox.askyesno("Export Complete", 
                                      f"Resume exported to {filename}\n\nOpen file?"):
                    webbrowser.open(result)
        
        except Exception as e:
            self.status_var.set(f"Export error: {str(e)}")
            messagebox.showerror("Export Error", str(e))
    
    def check_spelling(self):
        """Check spelling in the resume"""
        if not TEXT_ENHANCER_AVAILABLE:
            messagebox.showinfo("Spell Check", "Text enhancer module not available")
            return
        
        if not self.resume_text:
            messagebox.showinfo("Spell Check", "Generate a resume first")
            return
        
        try:
            # Check spelling
            corrected_text, corrections = text_enhancer.check_spelling(self.resume_text)
            
            if not corrections:
                messagebox.showinfo("Spell Check", "No spelling errors found")
                return
            
            # Create a dialog to show corrections
            corrections_window = tk.Toplevel(self.root)
            corrections_window.title("Spelling Corrections")
            corrections_window.geometry("400x300")
            corrections_window.configure(bg="#f0f0f0")
            
            # Create scrollable text area
            corrections_text = scrolledtext.ScrolledText(corrections_window, wrap=tk.WORD)
            ModernWidget.style_text(corrections_text)
            corrections_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add header
            corrections_text.insert(tk.END, "Spelling Corrections:\n\n")
            
            # Add each correction
            for mistake, correction in corrections:
                corrections_text.insert(tk.END, f"'{mistake}' should be '{correction}'\n")
            
            # Add apply button
            apply_button = tk.Button(corrections_window, text="Apply Corrections", 
                                  command=lambda: self.apply_spelling_corrections(corrected_text))
            ModernWidget.style_button(apply_button)
            apply_button.pack(pady=10)
        
        except Exception as e:
            messagebox.showerror("Spell Check Error", str(e))
    
    def apply_spelling_corrections(self, corrected_text):
        """Apply spelling corrections to the resume"""
        if not self.resume_text:
            return
        
        # Update resume text and preview
        self.resume_text = corrected_text
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, self.resume_text)
        
        # Update status
        self.status_var.set("Spelling corrections applied")
    
    def enhance_resume(self):
        """Enhance the resume text"""
        if not TEXT_ENHANCER_AVAILABLE:
            messagebox.showinfo("Enhance", "Text enhancer module not available")
            return
        
        if not self.resume_text:
            messagebox.showinfo("Enhance", "Generate a resume first")
            return
        
        try:
            # Update status
            self.status_var.set("Enhancing resume text...")
            self.root.update_idletasks()
            
            # Get job role for context
            job_role = self.job_role_var.get().strip()
            
            # Use threading to avoid freezing UI
            def enhance_thread():
                try:
                    # Try to use AI enhancement
                    if check_ollama_connection() and REQUESTS_AVAILABLE:
                        enhanced_text, explanation = text_enhancer.enhance_with_ai(
                            self.resume_text, job_role
                        )
                    else:
                        # Fall back to basic enhancement
                        enhanced_text, enhancements = text_enhancer.enhance_text(self.resume_text)
                        explanation = "Text enhanced with stronger language and improved clarity."
                    
                    # Update resume text and preview
                    self.resume_text = enhanced_text
                    
                    # Use after method to update UI from the main thread
                    self.root.after(0, self.update_preview_with_enhanced_text, enhanced_text, explanation)
                except Exception as e:
                    # Use after method to show error from the main thread
                    self.root.after(0, lambda: messagebox.showerror("Enhancement Error", str(e)))
            
            # Start enhancement in a separate thread
            enhancement_thread = threading.Thread(target=enhance_thread)
            enhancement_thread.daemon = True
            enhancement_thread.start()
            
        except Exception as e:
            self.status_var.set(f"Enhancement error: {str(e)}")
            messagebox.showerror("Enhancement Error", str(e))
    
    def update_preview_with_enhanced_text(self, enhanced_text, explanation):
        """Update preview with enhanced text (called from main thread)"""
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, enhanced_text)
        
        # Calculate ATS score
        self.calculate_ats_score()
        
        # Show explanation
        messagebox.showinfo("Text Enhanced", explanation)
        
        # Update status
        self.status_var.set("Resume enhanced successfully")
    
    def calculate_ats_score(self):
        """Calculate ATS score for the resume"""
        if not TEXT_ENHANCER_AVAILABLE or not self.resume_text:
            return
        
        try:
            # Calculate score
            score_results = text_enhancer.calculate_ats_score(self.resume_text)
            
            # Extract relevant information
            overall_score = score_results.get('overall', 0)
            
            # Determine rating
            if overall_score >= 85:
                rating = "Excellent"
            elif overall_score >= 70:
                rating = "Good"
            elif overall_score >= 50:
                rating = "Average"
            else:
                rating = "Needs Improvement"
                
            # Update score display
            self.ats_score_var.set(f"ATS Score: {overall_score} - {rating}")
            
            # Show feedback if score is below 70
            if overall_score < 70 and score_results.get('suggestions'):
                feedback_text = "\n".join(score_results['suggestions'])
                messagebox.showinfo("ATS Score Feedback", 
                                  f"Your resume scored {overall_score} - {rating}\n\nFeedback:\n{feedback_text}")
        
        except Exception as e:
            print(f"Error calculating ATS score: {str(e)}")

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeGeneratorApp(root)
    root.mainloop()