"""
Intent Classifier — BAAP AI v2
Rule-based first pass, designed to be upgraded to LLM-based classification.

Intents:
    greeting         — hellos, how-are-yous
    database_query   — SQL / table / column focused questions
    document_query   — questions about uploaded documents / files
    analytics_query  — chart, trend, visualisation requests
    hybrid_query     — spans both database AND document context
    general_chat     — everything else (capabilities, knowledge)
"""

import re
import logging
from typing import Literal

logger = logging.getLogger(__name__)

Intent = Literal[
    "greeting",
    "database_query",
    "document_query",
    "analytics_query",
    "hybrid_query",
    "general_chat",
]

# ── Keyword Sets ──────────────────────────────────────────────────────────────

_GREETING_PATTERNS = re.compile(
    r"\b(hi|hello|hey|good\s*(morning|afternoon|evening|day)|howdy|greetings|what'?s\s*up|sup|hiya)\b",
    re.IGNORECASE,
)

_DB_KEYWORDS = {
    "table", "tables", "column", "columns", "row", "rows", "database", "db",
    "query", "sql", "select", "count", "sum", "average", "avg", "total",
    "maximum", "minimum", "max", "min", "group by", "order by", "where",
    "join", "schema", "record", "records", "field", "fields", "entry",
    "entries", "revenue", "sales", "profit", "employee", "employees",
    "customer", "customers", "order", "orders", "product", "products",
    "invoice", "transaction", "transactions", "aggregate", "filter",
    "show me", "list all", "how many", "fetch", "retrieve", "get all",
}

_DOC_KEYWORDS = {
    "document", "documents", "file", "files", "pdf", "docx", "report",
    "uploaded", "text", "paragraph", "page", "pages", "summary", "summarize",
    "what does", "what did", "according to", "the document", "the report",
    "the file", "mention", "mentions", "stated", "states", "content",
    "section", "chapters", "article", "clause", "contract", "policy",
}

_ANALYTICS_KEYWORDS = {
    "chart", "charts", "graph", "plot", "visualise", "visualize",
    "trend", "trends", "growth", "decline", "over time", "month by month",
    "year by year", "bar chart", "line chart", "pie chart", "histogram",
    "comparison", "compare", "distribution", "breakdown",
}


# ── Classifier ────────────────────────────────────────────────────────────────

def classify_intent(question: str) -> Intent:
    """
    Classify the user's question into one of the supported intents.

    Args:
        question: Raw user input string.

    Returns:
        An Intent literal string.
    """
    text = question.lower().strip()
    words = set(re.findall(r"\b\w[\w\s]*\b", text))  # multi-word aware

    # 1. Greeting check (highest priority for short messages)
    if _GREETING_PATTERNS.search(text) and len(text.split()) <= 8:
        logger.debug("Intent: greeting")
        return "greeting"

    # 2. Score each domain
    db_score = sum(1 for kw in _DB_KEYWORDS if kw in text)
    doc_score = sum(1 for kw in _DOC_KEYWORDS if kw in text)
    analytics_score = sum(1 for kw in _ANALYTICS_KEYWORDS if kw in text)

    # 3. Hybrid: meaningful signals in both db AND doc
    if db_score >= 1 and doc_score >= 1:
        logger.debug("Intent: hybrid_query (db=%d, doc=%d)", db_score, doc_score)
        return "hybrid_query"

    # 4. Analytics (chart/trend but no doc signals)
    if analytics_score >= 1 and doc_score == 0:
        logger.debug("Intent: analytics_query (analytics=%d)", analytics_score)
        return "analytics_query"

    # 5. Pure database query
    if db_score >= 1:
        logger.debug("Intent: database_query (db=%d)", db_score)
        return "database_query"

    # 6. Pure document query
    if doc_score >= 1:
        logger.debug("Intent: document_query (doc=%d)", doc_score)
        return "document_query"

    # 7. General chat fallback
    logger.debug("Intent: general_chat")
    return "general_chat"


# ── Future hook: LLM-based override ──────────────────────────────────────────

def classify_intent_llm(question: str) -> Intent:
    """
    Reserved for LLM-based intent classification.
    Drop this in to replace or supplement classify_intent() when needed.
    """
    raise NotImplementedError("LLM-based intent classification not yet implemented.")
