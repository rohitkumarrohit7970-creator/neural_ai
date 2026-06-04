import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from groq import Groq
from matplotlib.figure import Figure
import gradio as gr
import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple

# --- Configuration & Setup ---
# Setup Groq API
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Global Data Cache
CACHED_DF = None

def load_and_clean_data(url: str) -> pd.DataFrame:
    """Loads and prepares the road accidents dataset with caching."""
    global CACHED_DF
    if CACHED_DF is not None:
        return CACHED_DF
        
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"Error loading data from URL: {e}. Falling back to local mock data.")
        data = {
            'state': ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh'],
            'accidents_2019': [21992, 237, 8350, 10007, 13899],
            'accidents_2020': [19509, 134, 6595, 8639, 11656],
            'accidents_2021': [21556, 283, 7411, 9553, 12375],
            'accidents_2022': [21249, 227, 7023, 10801, 13279],
            'accidents_2023': [19949, 287, 7421, 11014, 13468]
        }
        CACHED_DF = pd.DataFrame(data)
        return CACHED_DF
    
    # Cleaning columns
    rename_map = {
        '2019 Accidents': 'accidents_2019',
        '2020 Accidents': 'accidents_2020',
        '2021 Accidents': 'accidents_2021',
        '2022 Accidents': 'accidents_2022',
        '2023 Accidents': 'accidents_2023',
        'State': 'state'
    }
    df = df.rename(columns=rename_map)
    
    # Keep only relevant columns
    cols_to_keep = ['state', 'accidents_2019', 'accidents_2020', 'accidents_2021', 'accidents_2022', 'accidents_2023']
    df = df[cols_to_keep]
    
    # Filter out 'Total' or 'All India' rows to prevent double counting
    df = df[~df['state'].str.contains('Total|All India|Total States', case=False, na=False)]
    
    # Convert accident columns to numeric, forcing errors to NaN and then dropping them
    for col in ['accidents_2019', 'accidents_2020', 'accidents_2021', 'accidents_2022', 'accidents_2023']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna()
    
    CACHED_DF = df
    return df

# --- Logic Layer ---

class AccidentAnalyst:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.schema_info = self._get_schema_info()
        self.model = "llama-3.3-70b-versatile" # Highly capable model on Groq

    def _get_schema_info(self) -> str:
        """Returns a string description of the dataset schema for the LLM."""
        columns = self.df.columns.tolist()
        states = self.df['state'].unique().tolist()
        return f"""
        Dataset: Road Accidents in India (State-wise, 2019-2023)
        Columns: {', '.join(columns)}
        Sample States: {', '.join(states[:5])}
        The values in 'accidents_YYYY' columns represent the total number of road accidents in that state for that year.
        """

    def generate_pandas_query(self, user_question: str) -> Dict[str, Any]:
        """Uses Groq LLM to generate a safe pandas query string."""
        if not client:
            return {
                "query": "",
                "explanation": "Groq API key not configured. Please set GROQ_API_KEY.",
                "is_out_of_scope": True,
                "chart_type": "none"
            }

        prompt = f"""
        You are a data analyst. Based on the dataset schema below, write a Python snippet using 'df' to answer the question.
        
        Schema:
        {self.schema_info}
        
        Question: {user_question}
        
        Constraint: Return ONLY a valid JSON object with:
        1. "query": The pandas code to execute. IMPORTANT: If "chart_type" is "bar" or "line", the query MUST return a pandas Series or DataFrame where index is the category/time and values are the numbers.
        2. "explanation": What this query does in plain English.
        3. "is_out_of_scope": true if the question cannot be answered by this data (e.g. asking for deaths or crop yields), false otherwise.
        4. "chart_type": "bar", "line", or "none". Use "line" for trends over years (columns), "bar" for comparisons between states or categories.
        
        Guidelines for charts:
        - For trends over years for a state: "df[df['state'] == 'StateName'].iloc[0, 1:].astype(float)" (this returns a Series indexed by years)
        - For top states: "df.nlargest(5, 'accidents_2023').set_index('state')['accidents_2023']"
        
        Example JSON output:
        {{
            "query": "df[df['accidents_2023'] == df['accidents_2023'].max()][['state', 'accidents_2023']]",
            "explanation": "Identifies the state with the highest number of accidents in 2023.",
            "is_out_of_scope": false,
            "chart_type": "none"
        }}
        """
        
        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful data analyst that outputs only JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            return {
                "query": "",
                "explanation": f"Failed to generate query: {str(e)}",
                "is_out_of_scope": True,
                "chart_type": "none"
            }

    def execute_query(self, query_str: str) -> Any:
        """Executes the generated query string safely."""
        if not query_str:
            return None
        try:
            # Using eval in a controlled environment for the prototype
            return eval(query_str, {"df": self.df, "pd": pd, "np": np})
        except Exception as e:
            return f"Error: {str(e)}"

# --- Visualization ---

def create_chart(data: Any, chart_type: str):
    """Generates a matplotlib figure using explicit plotting for maximum reliability."""
    # Return an empty figure instead of None to prevent frontend TypeErrors
    fig = Figure(figsize=(10, 6))
    
    if chart_type == "none" or data is None:
        ax = fig.subplots()
        ax.text(0.5, 0.5, "No visualization required for this query.", 
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_axis_off()
        return fig
    
    print(f"DEBUG: Creating {chart_type} chart with data type: {type(data)}")
    
    try:
        ax = fig.subplots()
        
        # 1. Normalize data to a pandas Series
        plot_series = None
        if isinstance(data, (pd.DataFrame)):
            # If it's a dataframe, try to get the first numeric column or use the whole thing if it's 1D
            if data.shape[1] == 1:
                plot_series = data.iloc[:, 0]
            else:
                # Fallback: use the first numeric column
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    plot_series = data[numeric_cols[0]]
                else:
                    return None
        elif isinstance(data, pd.Series):
            plot_series = data
        elif isinstance(data, (int, float, np.number)):
            plot_series = pd.Series([data], index=["Result"])
        elif isinstance(data, list):
            plot_series = pd.Series(data)
        
        if plot_series is None or plot_series.empty:
            print("DEBUG: Plot series is empty or None")
            return None

        # 2. Explicit plotting (avoiding pandas wrapper for stability)
        x_values = [str(i) for i in plot_series.index]
        y_values = plot_series.values
        
        if chart_type == "bar":
            ax.bar(x_values, y_values, color='skyblue', edgecolor='navy', alpha=0.8)
        elif chart_type == "line":
            ax.plot(x_values, y_values, marker='o', linestyle='-', color='teal', linewidth=2, markersize=8)
            ax.grid(True, linestyle='--', alpha=0.6)

        # 3. Enhanced Labels and Titles
        ax.set_title(f"Data Visualization: {chart_type.capitalize()} Analysis", fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel("Number of Accidents", fontsize=12, labelpad=10)
        ax.set_xlabel("Category / Year", fontsize=12, labelpad=10)
        
        # Rotation for long labels
        if len(x_values) > 5:
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')

        fig.tight_layout()
        print("DEBUG: Chart created successfully")
        return fig
    except Exception as e:
        print(f"ERROR in create_chart: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- UI Components (Gradio) ---

# Dataset URL
DATA_URL = "https://data.opencity.in/dataset/6c8a27aa-a826-49a8-b017-9147621f8167/resource/3af0e158-4595-4118-b18a-f324662582cf/download/f2e6063b-95b8-4f7d-90f7-9128ed168689.csv"

def process_question(question: str):
    """Main pipeline for processing a user question."""
    # Initialization
    df = load_and_clean_data(DATA_URL)
    analyst = AccidentAnalyst(df)
    
    # 1. Generate Query
    response = analyst.generate_pandas_query(question)
    print(f"DEBUG: AI Explanation: {response['explanation']}")
    print(f"DEBUG: AI Query: {response['query']}")
    
    if response["is_out_of_scope"]:
        return f"### ⚠️ Out of Scope\n{response['explanation']}", None, "Out of Scope"
    
    # 2. Execute Query
    result = analyst.execute_query(response["query"])
    print(f"DEBUG: Execution Result Type: {type(result)}")
    
    # 3. Format Output
    try:
        if isinstance(result, (int, float, np.number)):
            # Format large numbers with commas
            formatted_result = f"### 📊 Total Result\n# {result:,.0f}"
        elif isinstance(result, (pd.Series, pd.DataFrame)):
            try:
                # Try to use to_markdown for a nice table
                formatted_result = f"### 📊 Result Data\n{result.to_markdown()}"
            except Exception:
                # Fallback to standard string representation if tabulate is missing or fails
                formatted_result = f"### 📊 Result Data\n```\n{str(result)}\n```"
        else:
            formatted_result = f"### 📊 Result\n{result}"
    except Exception as e:
        formatted_result = f"### 📊 Result Error\nError formatting output: {e}"

    answer = f"**Analysis:** {response['explanation']}\n\n{formatted_result}"
    chart = create_chart(result, response["chart_type"])
    provenance = f"**Query Executed:**\n```python\n{response['query']}\n```"
    
    return answer, chart, provenance

def launch_app():
    """Launches the Gradio interface."""
    with gr.Blocks(title="Talk to Government Data") as demo:
        gr.Markdown("# 🏛️ Talk to Government Data (Powered by Groq)")
        gr.Markdown("Ask questions about Road Accidents in India (2019-2023) in plain English.")
        
        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(
                    label="Ask a question", 
                    placeholder="e.g., Which state had the most accidents in 2023?",
                    lines=2
                )
                submit_btn = gr.Button("Analyze", variant="primary")
            
        with gr.Row():
            with gr.Column():
                output_answer = gr.Markdown(label="Response")
                output_chart = gr.Plot(label="Visualization")
                output_provenance = gr.Markdown(label="Audit Trail")

        submit_btn.click(
            fn=process_question,
            inputs=input_text,
            outputs=[output_answer, output_chart, output_provenance],
            api_name="analyze",
            queue=False
        )
        
        gr.Examples(
            examples=[
                "Which state had the highest number of accidents in 2023?",
                "Show the trend of accidents in Tamil Nadu from 2019 to 2023.",
                "How many people died in road accidents in 2023?",
                "What was the wheat production in Punjab in 2022?"
            ],
            inputs=input_text
        )

    # Use a dynamic port and explicitly disable queue to avoid ERR_ABORTED in preview environments
    demo.launch(
        server_name="127.0.0.1",
        show_error=True,
        debug=True,
        max_threads=10,
        theme=gr.themes.Soft()
    )

if __name__ == "__main__":
    launch_app()
