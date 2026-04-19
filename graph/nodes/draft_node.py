from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import AgentState

def draft_node(state: AgentState):
    """Generate a draft response based on the summary, classification, and tone."""
    print("--- DRAFTING RESPONSE ---")

    email_data     = state['email_data']
    summary        = state['summary']
    classification = state['classification']
    tone           = state.get('tone', 'Professional')

    tone_guide = {
        'Professional': 'Formal, clear, and respectful business language.',
        'Friendly':     'Warm, personable, and conversational while still polite.',
        'Concise':      'Short and to the point — no unnecessary words.',
        'Assertive':    'Confident, direct, and action-oriented.',
        'Casual':       'Relaxed and informal, like writing to a colleague you know well.',
    }
    tone_description = tone_guide.get(tone, tone_guide['Professional'])

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    system_prompt = f"""
You are a professional email assistant. Draft a reply to the following email.

Email classification: {classification}
Tone: {tone} — {tone_description}

Use the provided summary of the original email to address all key points.
Do NOT repeat the original email. Write only the reply body (no subject line).
"""

    user_content = (
        f"Original Email Summary:\n{summary}\n\n"
        f"Sender: {email_data['sender']}\n"
        f"Subject: {email_data['subject']}"
    )

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ])

    return {
        "draft_response": response.content,
        "status": "Needs Review"
    }
