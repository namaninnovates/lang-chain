import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# Use Google GenAI Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def setup_rag(documents_dir="documents", persist_dir="chroma_db"):
    print(f"Loading documents from {documents_dir}...")
    loader = DirectoryLoader(documents_dir, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()

    print(f"Loaded {len(documents)} documents. Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    print(f"Creating vector database with {len(docs)} chunks...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f"Vector database created successfully in {persist_dir}/")
    return vectorstore

if __name__ == "__main__":
    setup_rag()
