from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import AgentState

def summarize_node(state: AgentState):
    """Summarize the email content to extract key points."""
    print("--- SUMMARIZING EMAIL ---")
    
    email_data = state['email_data']
    content = email_data['body']
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = "Summarize the following email body. Extract key action items and main points in a concise bulleted list."
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=content)
    ])
    
    return {
        "summary": response.content,
        "status": "Summarized"
    }
