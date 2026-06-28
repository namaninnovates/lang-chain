from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from state import State
from nodes import (
    classify_intent,
    sales_agent,
    technical_agent,
    billing_agent,
    account_agent,
    general_agent,
    supervisor_agent
)
import sqlite3

def route_department(state: State):
    """Routing logic based on the intent."""
    return state.get("department", "general")

def check_high_risk(state: State):
    """Routing logic based on high_risk flag."""
    if state.get("high_risk", False):
        return "human_review"
    return END

def human_review_node(state: State):
    """
    This node serves as the interruption point.
    When this node is reached, LangGraph will interrupt if we set interrupt_before=["human_review"].
    Once approved/resumed, we just return the state.
    """
    # Assuming if it continues, it was approved.
    return {"approved": True}

def create_support_graph():
    builder = StateGraph(State)
    
    # Add Nodes
    builder.add_node("classify_intent", classify_intent)
    builder.add_node("sales", sales_agent)
    builder.add_node("technical", technical_agent)
    builder.add_node("billing", billing_agent)
    builder.add_node("account", account_agent)
    builder.add_node("general", general_agent)
    builder.add_node("supervisor", supervisor_agent)
    builder.add_node("human_review", human_review_node)
    
    # Add Edges
    builder.add_edge(START, "classify_intent")
    
    # Conditional edge from classify_intent to department agents
    builder.add_conditional_edges(
        "classify_intent",
        route_department,
        {
            "sales": "sales",
            "technical": "technical",
            "billing": "billing",
            "account": "account",
            "general": "general"
        }
    )
    
    # All department agents go to supervisor
    builder.add_edge("sales", "supervisor")
    builder.add_edge("technical", "supervisor")
    builder.add_edge("billing", "supervisor")
    builder.add_edge("account", "supervisor")
    builder.add_edge("general", "supervisor")
    
    # Supervisor goes to human review if high risk, else END
    builder.add_conditional_edges(
        "supervisor",
        check_high_risk,
        {
            "human_review": "human_review",
            END: END
        }
    )
    
    builder.add_edge("human_review", END)
    
    # Set up SQLite memory
    conn = sqlite3.connect("memory.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    
    # Compile graph with human-in-the-loop interruption
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["human_review"]
    )
    
    return graph

def save_graph_image(graph, filename="workflow_diagram.png"):
    try:
        # Requires httpx, draw_mermaid_png generates PNG from mermaid
        img_bytes = graph.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(img_bytes)
        print(f"Workflow diagram saved as {filename}")
    except Exception as e:
        print(f"Failed to generate workflow diagram image: {e}")

if __name__ == "__main__":
    graph = create_support_graph()
    save_graph_image(graph)
