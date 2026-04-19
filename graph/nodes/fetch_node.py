from graph.state import AgentState
from tools.gmail_tools import get_email_content

def fetch_node(state: AgentState):
    """Fetch the content of the email specified by email_id."""
    print(f"--- FETCHING EMAIL: {state['email_id']} ---")
    
    service = state['gmail_service']
    email_data = get_email_content(service, state['email_id'])
    
    if not email_data:
        return {"status": "Error", "email_data": {}}
    
    return {
        "email_data": email_data,
        "status": "Fetched"
    }
