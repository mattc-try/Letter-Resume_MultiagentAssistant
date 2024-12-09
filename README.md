# AI-Driven Resume and Cover Letter Generator

**Disclaimer**: This implementation is for educational purposes and may require further development for real-world applications.

This project is a simplified implementation of an AI-driven platform that generates tailored resumes and cover letters using multi-agent collaboration.

## Features

- **Content Generation Agent**: Generates resumes and cover letters based on user input.
- **Skill Matching Agent**: Extracts and matches user skills with job requirements.
- **Feedback and Refinement Agent**: Provides feedback on generated content for improvements.
- **User Interface**: Simple web interface for user interaction.

## Installation and Usage

1. **Clone the Repository**

   ```bash
   git clone https://github.com/mattc-try/Letter-Resume_MultiagentAssistant.git
   cd Letter-Resume_MultiagentAssistant
   ```
2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Download NLP Models**

   ```bash
   python -m spacy download en_core_web_sm
   ```
5. **Run the Application**

   ```bash
   python app.py
   ```
6. **Access the Web Interface**

   Open your browser and navigate to `http://localhost:5000`

# AI-Driven Multi-Agent Platform Implementation for Tailored Resumes and Cover Letters

Below is a simplified implementation of the AI-driven multi-agent platform as described. The project is organized into modules representing each agent and a simple user interface. The code is written in Python and uses popular libraries such as `transformers`, `spaCy`, and `Flask` for the web interface.

## Project Structure

```
project/
├── agents/
│   ├── content_generation_agent.py
│   ├── skill_matching_agent.py
│   ├── feedback_refinement_agent.py
│   └── __init__.py
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── styles.css
├── requirements.txt
└── README.md
```

## Additional Notes

- **Simplifications**: Due to the scope of a class project, the agents are simplified. For instance, the skill extraction uses basic NLP techniques and predefined labels.
- **Models**: GPT-2 is used instead of GPT-4 due to accessibility. In a real-world scenario, a more powerful model would be preferable.
- **Error Handling**: Minimal error handling is included. Additional checks and validations should be implemented for robustness.
- **Security**: The application runs in debug mode for development purposes. For production, disable debug mode and implement security best practices.


2: 

Skill User Researcher

Skills Job Description finder


1: 

Resume Strategist

Cover Letter Strategist



3: Feedback


3: Refinement

using user feedback and 3:


4:

likedin user profile

linkedin job description

user description

## License

Not yet done.
