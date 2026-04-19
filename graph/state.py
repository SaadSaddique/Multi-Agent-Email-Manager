from typing import TypedDict, List, Dict, Any, Annotated
import operator

class AgentState(TypedDict):
    email_id: str
    email_data: Dict[str, Any]
    classification: str  # 'Work', 'Personal', 'Newsletter', 'Spam'
    priority: str        # 'High', 'Medium', 'Low'
    sentiment: str       # 'Urgent', 'Positive', 'Neutral', 'Negative', 'Curious'
    summary: str
    draft_response: str
    status: str          # 'Needs Review', 'Approved', 'Rejected', 'Sent', 'Ignored'
    gmail_service: Any
    ui_mode: bool
    tone: str            # 'Professional', 'Friendly', 'Concise', 'Assertive', 'Casual'
    messages: Annotated[List[Dict[str, str]], operator.add]
