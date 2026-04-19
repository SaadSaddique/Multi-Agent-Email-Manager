import os
from dotenv import load_dotenv
from utils.gmail_auth import authenticate_gmail
from tools.gmail_tools import get_unread_emails
from graph.graph_builder import build_graph

def main():
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in .env file.")
        return

    print("--- STARTING EMAIL AGENT ---")
    
    # 1. Authenticate
    service = authenticate_gmail()
    if not service:
        print("Failed to authenticate with Gmail.")
        return
        
    # 2. Build Graph
    app = build_graph()
    
    # 3. Get Unread Emails
    unread_messages = get_unread_emails(service, max_results=3)
    
    if not unread_messages:
        print("No new unread emails found.")
        return
        
    print(f"Found {len(unread_messages)} unread emails.")
    
    # 4. Process each email
    for msg in unread_messages:
        initial_state = {
            "email_id": msg['id'],
            "gmail_service": service,
            "messages": []
        }
        
        print(f"\n>> Processing Message ID: {msg['id']}")
        try:
            for output in app.stream(initial_state):
                # output is a dict with node names as keys
                for key, value in output.items():
                    print(f"Node '{key}' completed.")
        except Exception as e:
            print(f"Error processing email {msg['id']}: {e}")

if __name__ == "__main__":
    main()
