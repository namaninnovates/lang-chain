# AI-Powered Customer Support Automation System

An intelligent support routing and response system built with LangGraph, LangChain, and OpenAI.

## Features
- **Intent Classification**: Automatically categorizes customer queries into Sales, Technical, Billing, or Account.
- **RAG Integration**: Specialized agents retrieve answers from dummy company documents (Policies, Pricing, Manuals, FAQs).
- **SQLite Memory**: Maintains conversation history for context-aware follow-ups (e.g. "What was my previous issue?").
- **Human-in-the-Loop**: High-risk queries (like refunds or cancellations) automatically pause the workflow and require human supervisor approval.
- **Supervisor Agent**: Polishes and validates responses before they are returned to the user.

## Setup Instructions

1. **Install Dependencies**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Set Environment Variables**:
Rename `.env.example` to `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
```

3. **Initialize the RAG Database**:
```bash
python rag_setup.py
```
This will read the documents from the `documents/` folder and create a local ChromaDB vector store.

4. **Generate the Workflow Diagram (Optional)**:
```bash
python graph.py
```
This compiles the graph and generates a `workflow_diagram.png` file representing the LangGraph architecture.

## Run Demonstration

Execute the demonstration script which automatically simulates the 5 required queries:
```bash
python demo.py
```
*Note: During Query 4 (Refund), you will be prompted in the terminal to press Enter to simulate the human-in-the-loop supervisor approval.*

## Project Structure
- `state.py`: Defines the TypedDict state (messages, intent, high_risk, context, etc.).
- `tools.py`: Contains the RAG retriever tool.
- `nodes.py`: Contains the intent classifier, department agents, and supervisor logic.
- `graph.py`: Builds the LangGraph workflow, routing, and SQLite memory checkpointing.
- `demo.py`: Runs the test cases.
- `documents/`: Contains the dummy company knowledge base.
