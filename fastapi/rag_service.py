from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv
import requests

load_dotenv()

class RAGService:
    def __init__(self):
        # Load documents from the syllabi directory
        self.loader = DirectoryLoader("data/syllabi/", glob="*.pdf")
        self.documents = self.loader.load()
        
        # Split documents into smaller chunks
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.texts = self.text_splitter.split_documents(self.documents)
        
        # Create embeddings and vector store
        self.embeddings = HuggingFaceEmbeddings()
        self.vectorstore = FAISS.from_documents(self.texts, self.embeddings)
        
        # Load Modal API details from environment variables
        self.modal_url = os.getenv('MODAL_BASE_URL')
        self.api_key = os.getenv('DSBA_LLAMA3_KEY')

    def query(self, question: str) -> dict:
        # Retrieve relevant documents
        relevant_docs = self.vectorstore.similarity_search(question, k=2)
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        # Prepare prompt for the Llama model
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        
        # Send request to Modal-served Llama model
        response = requests.post(
            f"{self.modal_url}/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": "NousResearch/Meta-Llama-3-8B-Instruct",
                "prompt": prompt,
                "max_tokens": 150
            }
        )
        
        # Process the response
        if response.status_code == 200:
            answer = response.json()['choices'][0]['text'].strip()
        else:
            answer = "Sorry, I couldn't generate an answer at this time."

        return {
            "answer": answer,
            "source_documents": [doc.page_content for doc in relevant_docs]
        }

rag_service = RAGService()