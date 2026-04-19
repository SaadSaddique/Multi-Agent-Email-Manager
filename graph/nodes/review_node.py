from graph.state import AgentState

def review_node(state: AgentState):
    """Wait for human approval of the draft (CLI mode)."""
    # If we are in UI mode, we might want to skip this or handle it differently
    if state.get("ui_mode"):
        return {"status": "Awaiting Review"}

    print("\n--- HUMAN REVIEW REQUIRED ---")
    print(f"Draft Response:\n{state['draft_response']}")
    print("-----------------------------\n")
    
    user_input = input("Approve this draft? (yes/no/edit): ").lower()
    
    if user_input == 'yes':
        return {"status": "Approved"}
    elif user_input == 'edit':
        new_draft = input("Enter the revised draft: ")
        return {"draft_response": new_draft, "status": "Approved"}
    else:
        return {"status": "Rejected"}
