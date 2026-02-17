from config import gemini_client, GEMINI_MODEL


def generate_answer(question, context):

    prompt = f"""
You are a professional placement preparation tutor.

Answer clearly and professionally using ONLY the provided context.

FORMAT STRICTLY AS:

Definition:
Clear definition in 1–2 sentences.

Explanation:
Explain in simple words.

Key Points:
• Point 1  
• Point 2  
• Point 3  

Rules:
- Use bullet points properly
- Use proper spacing
- Do NOT repeat citations unnecessarily
- Cite sources like [1], [2]
- Keep answer concise and readable

Context:
{context}

Question:
{question}

Answer:
"""

    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if not response or not response.text:
            return "I could not find this information in the provided notes."

        answer = response.text.strip()

        # Fix formatting
        answer = answer.replace("\\n", "\n")

        # Remove excessive blank lines
        lines = []
        for line in answer.split("\n"):
            line = line.strip()
            if line:
                lines.append(line)

        answer = "\n\n".join(lines)

        return answer

    except Exception:
        return "The assistant is temporarily unavailable."
