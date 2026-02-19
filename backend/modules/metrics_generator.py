"""
Module 4: Metrics Generator
Computes statistical KPIs from query results
"""
from typing import List, Dict, Any
from collections import Counter


def generate_metrics(columns: List[str], data: List[Dict]) -> Dict[str, Any]:
    if not data:
        return {
            "kpis": {"total_rows": 0, "total_columns": len(columns)},
            "numeric_stats": {},
            "text_stats": {},
        }

    total_rows = len(data)
    numeric_stats = {}
    text_stats = {}

    for col in columns:
        values = [row.get(col) for row in data]
        non_null = [v for v in values if v is not None]
        null_count = total_rows - len(non_null)

        # Try numeric
        try:
            nums = [float(v) for v in non_null]
            if nums:
                total = sum(nums)
                avg = total / len(nums)
                numeric_stats[col] = {
                    "count": len(nums),
                    "sum": round(total, 4),
                    "avg": round(avg, 4),
                    "min": round(min(nums), 4),
                    "max": round(max(nums), 4),
                    "null_count": null_count,
                }
        except (ValueError, TypeError):
            unique_vals = list(set(str(v) for v in non_null))
            top = Counter(str(v) for v in non_null).most_common(5)
            text_stats[col] = {
                "unique_count": len(unique_vals),
                "null_count": null_count,
                "top_values": [{"value": v, "count": c} for v, c in top],
            }

    # Headline KPI from first numeric column
    headline = None
    if numeric_stats:
        first = list(numeric_stats.keys())[0]
        s = numeric_stats[first]
        headline = {
            "column": first,
            "total_records": total_rows,
            "avg": s["avg"],
            "max": s["max"],
            "min": s["min"],
            "sum": s["sum"],
        }

    return {
        "kpis": {
            "total_rows": total_rows,
            "total_columns": len(columns),
            "numeric_columns": len(numeric_stats),
            "text_columns": len(text_stats),
            "headline": headline,
        },
        "numeric_stats": numeric_stats,
        "text_stats": text_stats,
    }
