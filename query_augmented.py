from config import gemini_client, GEMINI_MODEL
import time


def augment_query(question, memory_context):
    time.sleep(2)
    prompt = f"""
You are assisting with a retrieval system.

Rewrite the user's question into a clear, standalone query optimized for semantic document retrieval.

Guidelines:
- Expand abbreviations only if confident based on technical context.
- Do NOT invent meanings.
- Preserve original intent.
- If already clear, return unchanged.

Conversation history:
{memory_context}

User question:
{question}

Standalone retrieval query:
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text.strip()
