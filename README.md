
# AI-Driven Resume and Cover Letter Generator

**Disclaimer**: This implementation is for educational purposes and may require further development for real-world applications.

This project is a multi-agent AI platform that generates tailored resumes and cover letters based on job descriptions and user input, leveraging **CrewAI** for agent collaboration.

---

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
5. **Set the OpenAI API Key**
   Export your OpenAI API key as an environment variable (get your own not a charity):

   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

   Verify the key has been set correctly:

   ```bash
   echo $OPENAI_API_KEY
   ```
6. **Run the Application**

   ```bash
   python app.py
   ```
7. **Access the Web Interface**
   Open your browser and navigate to:

   ```
   http://localhost:5000
   ```

---

## Features

### 1. **Skill Matching Crew**

* **Job Researcher Agent** : Gathers job descriptions from input.
* **Candidate Profiler Agent** : Analyzes user skills and experience.
* **Skill Matcher Agent** : Matches candidate skills to job requirements for relevance.

### 2. **Content Generation Crew**

* **Resume Strategist Agent** : Creates a tailored resume that highlights matched skills and experience.
* **Cover Letter Strategist Agent** : Generates a customized cover letter aligned with the job description.

### 3. **Feedback and Refinement Crew**

* **Feedback Compiler Agent** : Aggregates feedback based on readability, grammar, sentiment, and structure.
* **Resume Refiner Agent** : Refines the resume to improve clarity, grammar, and readability.
* **Cover Letter Refiner Agent** : Optimizes the cover letter for grammar, sentiment, and overall quality.

### 4. **Feedback Metrics**

* **Readability Analysis** : Scores generated content for reading ease (e.g., Flesch Reading Ease, Gunning Fog).
* **Grammar Correction** : Corrects errors using a transformer-based grammar model.
* **Sentiment Analysis** : Measures subjectivity and emotional tone.
* **Structural Analysis** : Segments content and ensures keyword matching.

---

## Project Structure

```
project/
├── agents/
│   ├── content_generation_agent.py
│   ├── skill_matching_agent.py
│   ├── crewai_orchestrator.py
│   ├── feedback_refinement_agent.py
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── styles.css
├── requirements.txt
└── README.md
```

---

## License

MIT
