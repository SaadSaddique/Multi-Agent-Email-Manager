from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes.fetch_node import fetch_node
from graph.nodes.classify_node import classify_node
from graph.nodes.summarize_node import summarize_node
from graph.nodes.draft_node import draft_node
from graph.nodes.review_node import review_node
from graph.nodes.send_node import send_node

def should_process(state: AgentState):
    """Determine if we should continue processing based on classification."""
    if state['classification'] in ['Spam', 'Newsletter']:
        return "end"
    return "continue"

def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("fetch", fetch_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("draft", draft_node)
    workflow.add_node("review", review_node)
    workflow.add_node("send", send_node)
    
    # Define Edges
    workflow.set_entry_point("fetch")
    
    workflow.add_edge("fetch", "classify")
    
    # Conditional edge after classification
    workflow.add_conditional_edges(
        "classify",
        should_process,
        {
            "continue": "summarize",
            "end": END
        }
    )
    
    workflow.add_edge("summarize", "draft")
    workflow.add_edge("draft", "review")
    workflow.add_edge("review", "send")
    workflow.add_edge("send", END)
    
    return workflow.compile()
