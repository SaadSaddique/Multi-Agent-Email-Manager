import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import AgentState

def classify_node(state: AgentState):
    """Classify the email, assign priority, and detect sentiment."""
    print("--- CLASSIFYING EMAIL ---")

    email_data = state['email_data']
    content = (
        f"From: {email_data['sender']}\n"
        f"Subject: {email_data['subject']}\n\n"
        f"{email_data['body']}"
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    system_prompt = """
You are an expert email triage assistant. Analyse the following email and return a JSON object with exactly three keys:

1. "classification": one of Work | Personal | Newsletter | Spam
   - Work: Professional communications, tasks, meetings
   - Personal: Friends, family, non-work social
   - Newsletter: Informational subscriptions, updates
   - Spam: Unsolicited, promotional, junk

2. "priority": one of High | Medium | Low
   - High: Requires immediate attention or has a deadline
   - Medium: Should be handled today or tomorrow
   - Low: Can wait, no action urgently required

3. "sentiment": one of Urgent | Positive | Neutral | Negative | Curious
   - Urgent: Sender is stressed, demanding, or there is a deadline
   - Positive: Friendly, congratulatory, or good news
   - Neutral: Informational, no strong emotion
   - Negative: Complaints, frustration, or bad news
   - Curious: Questions, requests for information

Return ONLY the JSON — no markdown fencing, no extra text.
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=content)
    ])

    try:
        res_text = response.content.replace("```json", "").replace("```", "").strip()
        result = json.loads(res_text)
        return {
            "classification": result.get("classification", "Work"),
            "priority":       result.get("priority",       "Medium"),
            "sentiment":      result.get("sentiment",      "Neutral"),
            "status": "Classified"
        }
    except Exception as e:
        print(f"Error parsing classification: {e}")
        return {
            "classification": "Work",
            "priority":       "Medium",
            "sentiment":      "Neutral",
            "status": "Classification Failed"
        }
