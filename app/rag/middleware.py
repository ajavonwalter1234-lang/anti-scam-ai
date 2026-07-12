from typing import List, Dict, Any

def build_grounded_prompt(target_text: str, rag_matches: List[Dict[str, Any]]) -> str:
    """
    Constructs a prompt that prepends retrieved scam context before the target text.
    """
    if not rag_matches:
        # Fallback if vector store is offline or returns nothing
        return f"Analyze the following message for fraud or phishing risk:\n\n{target_text}"

    prompt_parts = [
        "You are an expert fraud and phishing analysis system.",
        "Below are examples of known scam tactics and messages from our database. Use these as context to determine if the target message exhibits similar fraudulent patterns.",
        "\n--- KNOWN SCAM CONTEXT ---"
    ]

    for match in rag_matches:
        # Assuming the indexer stores 'title', 'text', and 'similarity'
        metadata = match.get("metadata", {})
        title = metadata.get("title", "Unknown Scam Type")
        source = metadata.get("source", "Unknown Source")
        example_text = match.get("text", "")
        
        prompt_parts.append(f"\n[Type: {title} | Source: {source}]\nExample: {example_text}")

    prompt_parts.extend([
        "\n--- END CONTEXT ---",
        "\nBased on the patterns in the context above, analyze the following target message:",
        f"\nTARGET MESSAGE:\n{target_text}"
    ])

    return "\n".join(prompt_parts)
