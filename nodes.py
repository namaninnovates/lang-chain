from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from state import State
from tools import retrieve_company_info
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

class IntentClassification(BaseModel):
    department: str = Field(description="The department to route to: 'sales', 'technical', 'billing', 'account', or 'general' (for memory recall or unknown)")
    high_risk: bool = Field(description="True ONLY IF the request explicitly involves refunds, subscription cancellation, account closure, compensation, or escalation to management. Otherwise False.")

def classify_intent(state: State) -> State:
    """Categorizes the query and checks for high risk."""
    messages = state.get("messages", [])
    if not messages:
        return state
    
    # We only classify based on the latest user message
    latest_message = messages[-1].content
    
    prompt = f"""Analyze the following customer query.
    1. Route to 'sales' if it's about pricing, plans, or product information.
    2. Route to 'technical' if it's about app crashes, installation, configuration, or login errors (except password reset).
    3. Route to 'billing' if it's about invoices, refunds, or payment issues.
    4. Route to 'account' if it's about password reset, profile updates, or account activation/closure.
    5. Route to 'general' if they are asking about past conversations or something else.
    
    Query: {latest_message}
    """
    
    structured_llm = llm.with_structured_output(IntentClassification)
    result = structured_llm.invoke(prompt)
    
    return {"department": result.department, "high_risk": result.high_risk}

def _department_agent_node(state: State, department_name: str) -> State:
    messages = state.get("messages", [])
    latest_message = messages[-1].content if messages else ""
    
    # Retrieve relevant context from RAG
    context = retrieve_company_info.invoke(latest_message)
    
    system_prompt = f"""You are a specialized Customer Support Agent for the {department_name} department.
    Your goal is to help the customer based on the provided Knowledge Base context and the conversation history.
    If the context does not contain the answer, say you don't have that information.
    Be polite and professional.
    
    Knowledge Base Context:
    {context}
    """
    
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    return {"messages": [response], "context": context}

def sales_agent(state: State) -> State:
    return _department_agent_node(state, "Sales")

def technical_agent(state: State) -> State:
    return _department_agent_node(state, "Technical Support")

def billing_agent(state: State) -> State:
    return _department_agent_node(state, "Billing Support")

def account_agent(state: State) -> State:
    return _department_agent_node(state, "Account Support")

def general_agent(state: State) -> State:
    # Used for memory recall, doesn't strictly need RAG but we can provide it.
    system_prompt = "You are a general support assistant. Use the conversation history to answer the user's question (e.g., if they ask what their previous issue was). If you don't know, apologize."
    messages = state.get("messages", [])
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    return {"messages": [response]}

def supervisor_agent(state: State) -> State:
    """Validates and improves the response before it goes to the customer."""
    messages = state.get("messages", [])
    if not messages:
        return state
    
    # The last message is the draft from the department agent.
    draft_response = messages[-1].content
    user_query = messages[-2].content if len(messages) >= 2 else ""
    
    system_prompt = """You are a Support Supervisor. Review the Draft Response to the User Query.
    Correct any spelling/grammar mistakes, ensure the tone is professional and empathetic, and output ONLY the final polished response. Do not add any conversational filler like 'Here is the revised response'."""
    
    prompt = f"User Query: {user_query}\n\nDraft Response: {draft_response}"
    final_result = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    
    # We save the final polished response in state
    return {"final_response": final_result.content}
