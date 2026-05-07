"""Simplified prompt builder for cutoff-driven architecture."""


def build_prompt(user_prompt, system_prompt, rag_context=None):
    """Build a prompt from a system prompt and user input.

    Args:
        user_prompt: The user's question/query.
        system_prompt: Already-formatted system prompt from TemporalContext.
        rag_context: Optional list of RAG document strings.

    Returns:
        Complete prompt string ready for inference.
    """
    if rag_context:
        sources = "\n\nRelevant historical sources:\n"
        for i, doc in enumerate(rag_context[:5], 1):
            sources += f"{i}. {doc[:500]}\n"
        return f"{system_prompt}{sources}\n\nUser query: {user_prompt}\n\nAnalysis:"
    return f"{system_prompt}\n\nUser query: {user_prompt}\n\nAnalysis:"
