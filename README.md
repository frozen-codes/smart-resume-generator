# Enhanced Resume Generator

A feature-rich resume generator with AI-powered suggestions, multiple templates, and advanced export options.

## Features

- **Multiple Templates**: Choose from modern, classic, minimalist, and dark resume templates
- **Live Preview**: See your resume as you build it
- **Export Options**: Save your resume in TXT, HTML, DOCX, and PDF formats
- **AI-Powered Suggestions**: Get intelligent recommendations for skills and experience bullet points
- **LinkedIn Import**: Import data from LinkedIn profile exports
- **Grammar & Spell Checking**: Ensure your resume is error-free
- **QR Code Generation**: Add QR codes linking to your LinkedIn profile or personal website
- **ATS Optimization**: Get feedback on how your resume will perform with Applicant Tracking Systems
- **Dark Mode**: Create resumes with dark mode styling

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/frozen-codes/smart-resume-generator.git
   cd smart-resume-generator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. (Optional) Install the Ollama AI engine for AI-powered features:
   - Visit [Ollama](https://ollama.ai/) to download and install
   - Run the Ollama server locally
   - Download the recommended model:
     ```
     ollama pull qwen2.5:3b
     ```

## Usage

1. Run the application:
   ```
   python enhanced_resume_generator.py
   ```

2. Fill in your personal information, experience, education, and skills

3. Choose a template and export format

4. Generate your resume

5. Export the resume in your preferred format

## Optional Features

The application is designed with modularity in mind, so it will work even if some optional dependencies aren't installed. The following features require additional modules:

- **DOCX Export**: Requires `python-docx`
- **PDF Export**: Requires `fpdf`
- **QR Code Generation**: Requires `qrcode` and `pillow`
- **Advanced Grammar Checking**: Requires `language-tool-python`

## Project Structure

- `enhanced_resume_generator.py`: Main application file
- `resume_templates.py`: Templates for different resume styles
- `resume_export.py`: Export functionality for different formats
- `ai_suggestions.py`: AI-powered content suggestions
- `text_enhancer.py`: Grammar, spelling, and text improvement
- `qr_generator.py`: QR code generation utility
- `linkedin_import.py`: LinkedIn data import functionality

## License

MIT

## Acknowledgments

- This project uses [Ollama](https://ollama.ai/) for AI-powered suggestions
- Icons and styling inspired by modern UI design principles