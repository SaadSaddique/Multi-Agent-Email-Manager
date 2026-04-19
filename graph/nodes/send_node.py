from graph.state import AgentState
from tools.gmail_tools import send_message, mark_as_read

def send_node(state: AgentState):
    """Send the approved draft."""
    if state['status'] != 'Approved':
        print("--- SKIPPING SEND: Not Approved ---")
        return {"status": "Ignored"}
        
    print("--- SENDING EMAIL ---")
    
    email_data = state['email_data']
    service = state['gmail_service']
    
    result = send_message(
        service,
        to=email_data['sender'], # Replying to sender
        subject=f"Re: {email_data['subject']}",
        body=state['draft_response'],
        thread_id=email_data['threadId']
    )
    
    if result:
        mark_as_read(service, state['email_id'])
        return {"status": "Sent"}
    else:
        return {"status": "Send Failed"}
