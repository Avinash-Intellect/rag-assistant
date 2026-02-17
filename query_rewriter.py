from config import gemini_client, GEMINI_MODEL


def rewrite_query(original_query):

    prompt = f"""
Rewrite the following query to be more specific and explicit.
Expand abbreviations if possible.
Do not change meaning.

Query:
{original_query}

Rewritten Query:
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text.strip()
