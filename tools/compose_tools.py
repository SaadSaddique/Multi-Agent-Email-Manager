import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def compose_email(to: str, topic: str, tone: str = "Professional") -> dict:
    """
    Use GPT-4o to generate a full email (subject + body) from a topic and tone.
    Returns a dict with 'subject' and 'body'.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    system_prompt = f"""
You are an expert email writer. Write a complete email based on the user's topic.

Tone: {tone}
- Professional: Formal, clear, respectful business language.
- Friendly: Warm, personable, conversational but still polite.
- Concise: Short and to the point, no fluff.
- Assertive: Confident, direct, action-oriented.
- Casual: Relaxed and informal, like writing to a friend.

Return ONLY a JSON object with exactly two keys:
- "subject": the email subject line
- "body": the full email body (no subject line inside the body)

Do not include any markdown fencing or extra explanation.
"""

    user_message = f"Recipient: {to}\nTopic: {topic}"

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ])

    try:
        result = json.loads(response.content.strip())
        return {
            "subject": result.get("subject", ""),
            "body": result.get("body", "")
        }
    except Exception:
        # Fallback: return raw content as body
        return {
            "subject": f"Re: {topic}",
            "body": response.content
        }
