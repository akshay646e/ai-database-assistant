"""
Chat Engine — BAAP AI v2
Handles conversational responses: greetings, capability questions, general knowledge.
Uses a professional BAAP AI system prompt injected into every Gemini call.
"""

import logging
from core.llm import get_llm_model

logger = logging.getLogger(__name__)

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are BAAP AI, a professional AI Business Intelligence Assistant built for enterprise analytics.

Your capabilities:
- Analyze SQL databases (MySQL, PostgreSQL, SQLite) using natural language
- Answer questions about uploaded documents (PDF, Word, CSV, Excel)
- Generate data insights, business metrics, and interactive charts
- Provide strategic business recommendations based on data patterns
- Answer general business and analytics questions conversationally

Your personality:
- Professional, clear, and precise
- Proactively suggest next steps or follow-up queries
- When you don't have data context, explain what you can do and ask the user to connect a database or upload a document
- Never fabricate data — always be transparent about what you know vs. what requires a database query

Format guidelines:
- Use bullet points for lists
- Keep answers concise but complete
- For greetings, be warm and briefly introduce your capabilities
"""


# ── Engine ────────────────────────────────────────────────────────────────────

def handle_chat(question: str) -> str:
    """
    Generate a conversational response using Gemini with the BAAP AI system prompt.

    Args:
        question: The user's free-form question or message.

    Returns:
        A natural language response string.
    """
    model = get_llm_model()

    full_prompt = f"""{SYSTEM_PROMPT}

USER: {question}

BAAP AI:"""

    try:
        response = model.generate_content(full_prompt)
        answer = response.text.strip()
        logger.info("Chat engine responded successfully.")
        return answer

    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "exhausted" in error_str.lower():
            logger.warning("Chat engine hit rate limit: %s", error_str)
            return (
                "I'm receiving too many requests right now. "
                "Please wait a moment and try again."
            )
        logger.error("Chat engine error: %s", error_str)
        return f"I encountered an error processing your message. Please try again."


def handle_greeting(question: str) -> str:
    """
    Specific handler for greetings — lightweight, fast response.
    Falls back to handle_chat if LLM errors out.
    """
    greetings_prompt = f"""{SYSTEM_PROMPT}

The user just greeted you. Respond warmly in 2-3 sentences, introduce yourself as BAAP AI, 
and briefly mention 2-3 key things you can help with. Be concise and inviting.

USER: {question}

BAAP AI:"""

    model = get_llm_model()
    try:
        response = model.generate_content(greetings_prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning("Greeting handler fallback: %s", str(e))
        return (
            "👋 Hello! I'm **BAAP AI**, your Business Intelligence Assistant. "
            "I can help you query databases with plain English, analyze uploaded documents, "
            "and generate charts and insights. How can I assist you today?"
        )
