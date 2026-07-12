from typing import List, Dict, Any, Optional
import os

DEFAULT_MAX_PROMPT_CHARS = int(os.getenv("PROMPT_MAX_CHARS", "4000"))
DEFAULT_PER_EXAMPLE_CHARS = int(os.getenv("PER_EXAMPLE_MAX_CHARS", "800"))


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    # try to cut at a sentence boundary if possible
    cutoff = text.rfind('.', 0, max_chars)
    if cutoff == -1 or cutoff < max_chars // 2:
        return text[:max_chars-3] + '...'
    return text[:cutoff+1]


def build_grounded_prompt(target_text: str,
                          rag_matches: List[Dict[str, Any]],
                          max_prompt_chars: Optional[int] = None,
                          per_example_max_chars: Optional[int] = None) -> str:
    """
    Constructs a prompt that prepends retrieved scam context before the target text.

    This function enforces a simple prompt-size guarding strategy:
      - per_example_max_chars: truncate each retrieved example to this many characters
      - max_prompt_chars: cap the final prompt length; if exceeded, include as many examples as fit
        and append a truncation notice.

    This is a lightweight, deterministic guard suitable for prototyping. For production,
    consider token-counting based on the target model's tokenizer and/or summarization of
    long context documents.
    """
    if max_prompt_chars is None:
        max_prompt_chars = DEFAULT_MAX_PROMPT_CHARS
    if per_example_max_chars is None:
        per_example_max_chars = DEFAULT_PER_EXAMPLE_CHARS

    if not rag_matches:
        # Fallback if vector store is offline or returns nothing
        return f"Analyze the following message for fraud or phishing risk:\n\n{target_text}"

    prompt_parts = [
        "You are an expert fraud and phishing analysis system.",
        "Below are examples of known scam tactics and messages from our database. Use these as context to determine if the target message exhibits similar fraudulent patterns.",
        "\n--- KNOWN SCAM CONTEXT ---"
    ]

    current_length = sum(len(p) for p in prompt_parts) + len(target_text)
    included_any = False

    for match in rag_matches:
        if current_length > max_prompt_chars:
            break

        metadata = match.get("metadata", {})
        title = metadata.get("title", "Unknown Scam Type")
        source = metadata.get("source", "Unknown Source")
        example_text = match.get("text", "")

        truncated_example = _truncate_text(example_text, per_example_max_chars)
        block = f"\n[Type: {title} | Source: {source}]\nExample: {truncated_example}"
        # if adding this block would exceed the prompt budget, stop
        if current_length + len(block) > max_prompt_chars:
            break

        prompt_parts.append(block)
        current_length += len(block)
        included_any = True

    if not included_any:
        # nothing fit within budget; fall back to including only the target text and a short note
        return f"Analyze the following message for fraud or phishing risk (context omitted due to length limits):\n\n{target_text}"

    prompt_parts.extend([
        "\n--- END CONTEXT ---",
        "\nBased on the patterns in the context above, analyze the following target message:",
        f"\nTARGET MESSAGE:\n{target_text}"
    ])

    final_prompt = "\n".join(prompt_parts)

    # enforce the hard cap one last time; if exceeded, truncate the context portion conservatively
    if len(final_prompt) > max_prompt_chars:
        # preserve header and target, chop middle by truncating context to fit
        header = "You are an expert fraud and phishing analysis system.\n--- KNOWN SCAM CONTEXT ---\n"
        footer = f"\n--- END CONTEXT ---\n\nTARGET MESSAGE:\n{target_text}"
        budget_for_context = max_prompt_chars - len(header) - len(footer)
        if budget_for_context <= 0:
            # as a last resort, return a minimal prompt
            return f"Analyze the following message for fraud or phishing risk (context omitted due to strict length limits):\n\n{target_text}"
        # build context by joining truncated examples until budget
        context_parts = []
        for match in rag_matches:
            example_text = _truncate_text(match.get("text", ""), per_example_max_chars)
            part = f"[Type: {match.get('metadata', {}).get('title','')}] Example: {example_text}\n---\n"
            if sum(len(p) for p in context_parts) + len(part) > budget_for_context:
                break
            context_parts.append(part)
        context_str = "\n".join(context_parts)
        final_prompt = header + context_str + footer
        # if still too long, truncate the context string forcibly
        if len(final_prompt) > max_prompt_chars:
            allowed = max_prompt_chars - len(header) - len(footer)
            context_str = context_str[:max(0, allowed-3)] + "..."
            final_prompt = header + context_str + footer

    return final_prompt
