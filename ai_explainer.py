import os
import google.generativeai as genai
from email_model import NormalizedEmail

# Configure Gemini
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash"
)


def explain_email(
    email: NormalizedEmail,
    category: str,
    rule_id: str
) -> str:
    """
    Gemini explains a PRE-DETERMINED decision.
    It does NOT classify or override rules.
    """

    prompt = f"""
You are explaining an email classification to a non-technical user.

Email details:
Sender: {email.sender}
Subject: {email.subject}
Snippet: {email.snippet}

System decision (already final):
Category: {category}
Rule applied: {rule_id}

Explain in 3 short bullet points:
- Why this email was classified this way
- What the user should do (if anything)
- Whether this needs urgent attention

Rules:
- Do NOT change the category
- Do NOT invent new reasons
- Do NOT mention AI or models
- Only explain the given decision
Do not give long introduction. Just come to bullet points directly.
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 450
        }
    )

    return response.text.strip()
