"""
Module 6: Insight Generator — uses Gemini to analyze results
"""
import os
import json
import re
import google.generativeai as genai
from typing import List, Dict, Any


def generate_insights(
    question: str,
    sql: str,
    data: List[Dict],
    metrics: Dict,
) -> List[str]:

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ["Set GEMINI_API_KEY in .env to enable AI insights."]

    if not data:
        return ["No data was returned by this query."]

    genai.configure(api_key=api_key)
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)

    kpis = metrics.get("kpis", {})
    numeric_stats = metrics.get("numeric_stats", {})
    sample = data[:15]

    prompt = f"""You are a data analyst. Analyze this query result and give 4 concise insights.

QUESTION: {question}
SQL: {sql}
TOTAL ROWS: {kpis.get('total_rows', 0)}
SAMPLE DATA: {json.dumps(sample, default=str)}
STATS: {json.dumps(numeric_stats, default=str)}

Rules:
- Each insight = 1-2 sentences max
- Be specific with numbers
- Focus on patterns, outliers, trends
- Return ONLY a JSON array of strings like: ["insight1", "insight2", "insight3", "insight4"]
- No markdown, no extra text, just the JSON array

JSON ARRAY:"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())[:5]
        # fallback: split lines
        return [l.strip().lstrip("-•0123456789. ") for l in text.split("\n") if l.strip()][:5]
    except Exception as e:
        return [f"Could not generate insights: {e}"]
