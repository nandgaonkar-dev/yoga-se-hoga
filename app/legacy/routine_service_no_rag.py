"""
Pre-RAG routine generation, kept as a reference point for how the project evolved.

Not used by the live API (app/main.py only serves the RAG path) — this is the
Week 2 implementation: structured output + retry, no retrieval. Reuses
`_generate_with_retry` from app.routine_service since that helper is generic
(call Groq, validate, retry) and isn't RAG-specific.
"""

from app.config import settings
from app.routine_service import _generate_with_retry


def generate_routine_locally(experience_level: str, time_available: int, goal: str,
                              injuries: str | None = None, max_retries: int = settings.default_max_retries):
    user_prompt = (
        f"Experience level: {experience_level}\n"
        f"Time available: {time_available} minutes\n"
        f"Goal: {goal}\n"
        + (f"Injuries or limitations: {injuries}\n" if injuries else "")
        + "Please generate a yoga routine based on the above information."
    )

    messages = [
        {"role": "system", "content": "You are a helpful yoga instructor."},
        {"role": "user", "content": user_prompt}
    ]

    return _generate_with_retry(messages, max_retries)
