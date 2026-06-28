from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    intent: str
    high_risk: bool
    context: str
    department: str
    approved: bool
    final_response: str
