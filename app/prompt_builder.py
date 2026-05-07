from datetime import datetime
from app.temporal_profile import TemporalProfile


def build_prompt(user_prompt, profile, rag_context=None, current_year=None):
    system = profile.format_system_prompt(current_year)
    if not system:
        system = f"You are a historical reasoning model with a knowledge cutoff of {profile.cutoff_year}."

    if rag_context:
        system += "\n\nRelevant historical sources:\n"
        for i, doc in enumerate(rag_context[:5], 1):
            system += f"{i}. {doc[:500]}\n"

    return f"{system}\n\nUser query: {user_prompt}\n\nAnalysis:"