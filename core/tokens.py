# shayan.txt
"""Token optimization utilities"""

import hashlib
import re

# Approx: 1 token ~ 4 chars for Persian/English mix
def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)

def truncate_text(text: str, max_tokens: int = 500) -> str:
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."

def hash_prompt(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()[:16]

def extract_keywords(text: str) -> list[str]:
    # Simple keyword extraction for RAG
    words = re.findall(r'\w{3,}', text.lower())
    stop = {"این","است","برای","با","از","به","که","را","در","یک","و","چه","چطور"}
    return [w for w in words if w not in stop][:8]

def is_simple_query(text: str) -> bool:
    """Simple greetings that don't need LLM"""
    t = text.strip().lower()
    simples = ["سلام", "hi", "hello", "salam", "چطوری", "خوبی", "مرسی", "thanks", "bye"]
    return any(t == s or t.startswith(s + " ") for s in simples) or len(t.split()) <= 2
