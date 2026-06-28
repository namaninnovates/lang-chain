from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

# Initialize the vector store connection
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

@tool
def retrieve_company_info(query: str) -> str:
    """
    Search the company knowledge base (Policies, Pricing, Technical Manuals, FAQs) for information relevant to the query.
    Use this tool whenever you need to answer a customer question using official company documents.
    """
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant information found in the knowledge base."
    
    return "\n\n".join([doc.page_content for doc in docs])
