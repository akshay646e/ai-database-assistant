import json
import re
from typing import List, Dict, Any
from core.llm import get_llm_model


def generate_suggestions(
    question: str,
    schema: Dict,
    data: List[Dict],
) -> List[str]:

    try:
        model = get_llm_model()
    except ValueError:
        return []

    tables = ", ".join(schema.keys())
    sample = json.dumps(data[:5], default=str)

    prompt = f"""You are a database analytics assistant. A user queried their database.

THEIR QUESTION: {question}
AVAILABLE TABLES: {tables}
SAMPLE RESULT: {sample}

Generate 5 smart follow-up questions they might ask next.
Rules:
- Natural English questions
- Relevant to the data they just saw
- Mix of simple and complex queries
- Return ONLY a JSON array: ["q1?", "q2?", "q3?", "q4?", "q5?"]
- No markdown, just the JSON array

JSON ARRAY:"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())[:5]
        return [l.strip().lstrip("-•0123456789. ") for l in text.split("\n") if l.strip()][:5]
    except Exception as e:
        if "429" in str(e) or "exhausted" in str(e).lower():
            return ["API rate limit reached. Suggestion generation skipped."]
        return []
