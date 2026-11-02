# shayan.txt
"""Lightweight toxicity detection (no LLM call)"""

import re

# Patterns that indicate needing AI moderation
TOXIC_PATTERNS = [
    r"(کسکش|کیر|جنده|حرومزاده)",  # keep minimal
]

def quick_toxicity_check(text: str) -> tuple[bool, float]:
    """Returns (is_toxic, confidence) without LLM"""
    if not text:
        return False, 0.0
    lower = text.lower()
    # Rule 1: repeated chars spam
    if re.search(r"(.)\1{5,}", lower):
        return True, 0.6
    # Rule 2: excessive caps
    if len(text) > 20 and sum(1 for c in text if c.isupper()) / len(text) > 0.7:
        return True, 0.5
    return False, 0.0

def should_use_ai_moderation(text: str) -> bool:
    # Only call AI for borderline cases, not every message
    toxic, conf = quick_toxicity_check(text)
    return conf > 0.5 and conf < 0.9
