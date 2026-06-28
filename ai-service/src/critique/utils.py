# ─────────────────────────────────────────────────────────────────
# src/critique/utils.py
# ─────────────────────────────────────────────────────────────────
#
# Helper utilities for the Self-Critique Layer.
# ─────────────────────────────────────────────────────────────────

def deduplicate_preserve_order(items: list) -> list:
    """
    Deduplicates a list of elements while preserving their original insertion order.
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
