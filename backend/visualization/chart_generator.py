from typing import List, Dict, Any

COLORS = [
    "#6c47ff", "#22c55e", "#3b82f6", "#f97316",
    "#a855f7", "#14b8a6", "#f43f5e", "#eab308",
    "#0ea5e9", "#8b5cf6", "#ec4899", "#84cc16",
]

def generate_chart_config(columns: List[str], data: List[Dict], question: str) -> Dict[str, Any]:
    if not data or not columns:
        return {"chart_type": "bar", "labels": [], "datasets": []}

    q = question.lower()
    numeric_cols = _get_numeric_cols(columns, data)
    text_cols = [c for c in columns if c not in numeric_cols]

    # Detect chart type
    if any(k in q for k in ["trend", "over time", "monthly", "daily", "yearly", "history", "timeline"]):
        chart_type = "line"
    elif any(k in q for k in ["share", "percentage", "proportion", "distribution", "breakdown", "pie"]):
        chart_type = "pie"
    elif not numeric_cols:
        chart_type = "bar"
    elif len(data) <= 10 and text_cols:
        chart_type = "pie"
    else:
        chart_type = "bar"

    # Build labels and datasets
    label_col = text_cols[0] if text_cols else columns[0]
    labels = [str(row.get(label_col, "")) for row in data]

    datasets = []
    value_cols = numeric_cols[:3] if numeric_cols else []

    for i, col in enumerate(value_cols):
        vals = [row.get(col) for row in data]
        try:
            vals = [float(v) if v is not None else 0 for v in vals]
        except (ValueError, TypeError):
            continue

        color = COLORS[i % len(COLORS)]
        datasets.append({
            "label": col,
            "data": vals,
            "backgroundColor": [COLORS[j % len(COLORS)] for j in range(len(vals))] if chart_type == "pie" else color,
            "borderColor": color,
            "borderWidth": 2 if chart_type == "line" else 0,
            "borderRadius": 6 if chart_type == "bar" else 0,
            "tension": 0.4,
            "fill": False,
        })

    return {
        "chart_type": chart_type,
        "labels": labels,
        "datasets": datasets,
        "label_col": label_col,
        "value_cols": value_cols,
    }


def _get_numeric_cols(columns: List[str], data: List[Dict]) -> List[str]:
    result = []
    for col in columns:
        try:
            sample = [row.get(col) for row in data[:30] if row.get(col) is not None]
            if sample:
                [float(v) for v in sample]
                result.append(col)
        except (ValueError, TypeError):
            pass
    return result
