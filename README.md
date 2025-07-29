# Research_Agent
The Generative AI Research Assistant is an intelligent tool built with LangGraph, Groq's LLaMA 3, and Tavily Search API that automates topic research, document summarization, and confidence scoring


markdown
Copy code
## Generative AI Research Agent

This is an intelligent AI assistant that helps you **do research** on any topic. It reads your question, searches online and in academic papers, and gives you a detailed, clear answer — just like a real research assistant.

---

# What It Can Do

✅ Understand your research topic  
✅ Break it into smaller questions  
✅ Search the internet and research papers  
✅ Read documents and find useful information  
✅ Write a full research report with sources  
✅ Give confidence scores for each answer  
✅ Show everything in a simple web app  

---

# Example Research Question

> "What is the impact of AI on healthcare diagnostics in the last 5 years?"

The agent will:
- Plan the research steps
- Search online and in research papers
- Combine all findings
- Write a clean report with citations and confidence levels

---

# What You’ll See

- **Text box** to type your question  
- **Live progress** get the output 
- **Downloadable report** with all findings  
- **Easy-to-use web interface**

---

# Tools Used

- **LangGraph** 
- **Python**   
- **Tavily API**
- **arXiv / Semantic Scholar** 
- **Streamlit**

---

# How to Use

## 1. Clone the Project

git clone https://github.com/yourname/research-agent
cd research-agent

## 2. Install Requirements
pip install -r requirements.txt

## 3. Add Your API Keys
Create a .env file and add:

TAVILY_API_KEY = "your_api_key"

GROQ_API_KEY = "your_groq_key"

## 4. Run the Web App
streamlit run interfaces/streamlit_ui.py






