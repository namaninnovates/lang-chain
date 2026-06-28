import os
from langchain_core.messages import HumanMessage
from graph import create_support_graph

def run_demo():
    print("="*50)
    print("Initializing Customer Support Automation System Demo")
    print("="*50)
    
    graph = create_support_graph()
    thread_id = "customer_123"
    config = {"configurable": {"thread_id": thread_id}}
    
    queries = [
        "What are the pricing plans available for your software?",
        "I forgot my account password.",
        "My application crashes whenever I upload a file.",
        "I need a refund for my annual subscription.",
        "What was my previous support issue?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[Query {i}]: {query}")
        
        # Invoke the graph
        events = graph.stream(
            {"messages": [HumanMessage(content=query)]},
            config,
            stream_mode="values"
        )
        
        for event in events:
            # We just iterate through the state changes
            # Optionally print intermediate routing steps
            pass
        
        # Get the final state
        state = graph.get_state(config)
        
        # Check if the graph was interrupted for human review
        if state.next and "human_review" in state.next:
            print("\n>>> ⚠️ HIGH RISK REQUEST DETECTED: HUMAN REVIEW REQUIRED ⚠️ <<<")
            print("Supervisor Review Needed. Do you approve this request? (Press Enter to approve)")
            
            # In a real app, this would block and wait for a button click or API call.
            # For demo purposes, we automatically simulate an approval after a mock pause.
            input("(Press Enter to simulate human approval...)")
            
            # Resume the graph with the approval
            events = graph.stream(None, config, stream_mode="values")
            for event in events:
                pass
            
            # Get updated state
            state = graph.get_state(config)
            print(">>> ✅ Supervisor Approved! Resume workflow. <<<")
        
        # Print the final response and intent
        final_state = state.values
        department = final_state.get("department")
        final_response = final_state.get("final_response")
        
        print(f"Routed to: {department.upper() if department else 'UNKNOWN'}")
        print(f"Final Response: {final_response}")
        print("-" * 50)

if __name__ == "__main__":
    run_demo()
