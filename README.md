# 🏛️ Talk to Government Data

A natural-language data analysis tool designed for government officials to interact with open datasets using plain English. Built as part of the **Neural City GenAI Intern Screening Assignment**.

## 🚀 Overview

This application allows non-technical users to query complex government datasets (CSV format) by asking questions in natural language. The system translates these questions into safe, executable Python code, performs the analysis, and provides both a human-readable explanation and visual charts.

**Dataset Integrated:** [Road Accidents in India (2019-2023)](https://data.opencity.in/dataset/road-accidents-in-india-2023)

## ✨ Key Features

- **Natural Language to Code**: Powered by Llama 3 (via Groq) to translate English questions into precise Pandas queries.
- **Safety & Trust**: 
  - **No Hallucinations**: If a question is outside the data's scope (e.g., asking for deaths when only accident counts exist), the tool explicitly says so.
  - **Audit Trail**: Every response includes the exact code executed for transparency.
- **Dynamic Visualization**: Automatically generates bar charts for comparisons and line charts for trends.
- **Robust Backend**: Thread-safe Matplotlib implementation and optimized data caching for speed.

## 🛠️ Tech Stack

- **LLM Engine**: Groq (Llama-3.3-70b-versatile)
- **Framework**: Gradio (Web Interface)
- **Data Processing**: Pandas & NumPy
- **Visualization**: Matplotlib
- **Language**: Python 3.10+

## 📥 Installation

1. **Clone the repository**:
   ```bash
   cd neural_ai
   ```

2. **Set up Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install pandas numpy matplotlib seaborn groq gradio tabulate
   ```

## 🚦 How to Run

1. **Set your Groq API Key**:
   ```bash
   export GROQ_API_KEY="your_api_key_here"
   ```

2. **Launch the Application**:
   ```bash
   python3 app_prototype.py
   ```

3. **Access the UI**:
   Open `http://127.0.0.1:7860` (or the port shown in your terminal) in your browser.

## 📝 Example Questions

- **Trends**: *"Show the trend of accidents in Tamil Nadu from 2019 to 2023."*
- **Rankings**: *"Which 5 states had the most accidents in 2023?"*
- **Statistics**: *"What was the total number of accidents in India in 2023?"*
- **Safety Check**: *"How many people died in road accidents in 2023?"* (Result: Out of Scope)

## 📂 Project Structure

- `app_prototype.py`: Main application logic and UI.
- `design_note.md`: Detailed explanation of architecture, scaling, and safety decisions.
- `coding_solutions.md`: Reference for coding patterns followed.
- `coding_sign.md`: Quality guidelines for generated code.

---
*Developed for the Neural City GenAI Intern Screening Assignment.*
