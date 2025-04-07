# Smart Resume Generator

An intelligent and feature-rich application for creating professional resumes with AI-powered suggestions, multiple templates, and advanced formatting options.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

## 🌟 Features

- **🎨 Multiple Template Selection**: Choose from modern, classic, minimalist, and dark mode templates
- **👁️ Live Resume Preview**: See how your resume looks as you edit in real-time
- **📤 Export Options**: Export as TXT, HTML, DOCX, and PDF
- **🤖 AI-Powered Suggestions**: Get intelligent suggestions for skills and experience using Ollama
- **🔗 LinkedIn Integration**: Import your professional data directly from LinkedIn exports
- **✍️ Text Enhancement**: Spell checking, grammar checking, and text improvement
- **📱 QR Code Generation**: Add QR codes linking to your LinkedIn profile or website
- **📊 ATS Score Rating**: Get feedback on ATS compatibility with optimization suggestions
- **🌙 Dark Mode**: Create professional dark-themed resumes

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- Tkinter (usually comes with Python)
- [Ollama](https://ollama.ai/) for AI features

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/frozen-codes/smart-resume-generator.git
   cd smart-resume-generator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Ollama (for AI features):
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull qwen2.5:3b
   ollama serve
   ```

## 💻 Usage

1. Run the enhanced version with all features:
   ```bash
   python enhanced_resume_generator.py
   ```

2. For a simpler version without optional dependencies:
   ```bash
   python simple_resume_generator.py
   ```

### Application Guide

1. **👤 Personal Information**
   - Fill in your basic details
   - Add contact information and links

2. **💼 Experience**
   - Add work history using Markdown
   - Get AI-powered suggestions for bullet points
   - Format dates and company information

3. **🎓 Education**
   - Add educational background
   - Include relevant certifications

4. **🛠️ Skills**
   - List technical and soft skills
   - Use AI suggestions based on job role
   - Organize by categories

5. **📝 Template & Export**
   - Choose from multiple templates
   - Select export format
   - Enable dark mode or QR code options

6. **📥 LinkedIn Import**
   - Import from LinkedIn export files
   - Auto-populate all sections
   - Review and edit imported data

7. **✨ Enhancement Tools**
   - Run spell check
   - Improve text quality
   - Check ATS compatibility

## 🏗️ Project Structure

```
smart-resume-generator/
├── enhanced_resume_generator.py  # Main application
├── simple_resume_generator.py    # Basic version
├── resume_templates.py          # Template definitions
├── resume_export.py            # Export functionality
├── ai_suggestions.py           # AI integration
├── text_enhancer.py           # Text improvement
├── qr_generator.py            # QR code generation
├── linkedin_import.py         # LinkedIn integration
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

## 🔧 Troubleshooting

- **AI Features**: Ensure Ollama is running (`http://localhost:11434`)
- **Export Issues**: Check required libraries for each format
- **LinkedIn Import**: Use official LinkedIn data export files
- **Dependencies**: Install all optional modules for full functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for the AI model integration
- [Python-docx](https://python-docx.readthedocs.io/) for DOCX export
- [FPDF](http://fpdf.org/) for PDF generation
- [QRCode](https://pypi.org/project/qrcode/) for QR code generation

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.