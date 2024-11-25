from fastapi import FastAPI
import syllabi_store as sc
import logging
import os
import requests
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import BaseModel
from typing import List
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.llms.base import LLM
from typing import Optional, List
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from transformers import pipeline
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFacePipeline
#from huggingface_hub import login

import json

os.environ['KMP_DUPLICATE_LIB_OK']='True'


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s -  %(module)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

app = FastAPI()
logger.info("Loading Store")
s_store = sc.SyllabiStore()
MAX_DOCS=5
logger.info("Store Loaded")

from langchain.llms.base import LLM
from typing import Optional


class SyllabusSearchRetriever(BaseRetriever):
    global s_store

    def _get_relevant_documents(self, query: str) -> list[Document]:
        """
        Retrieve the top `k` relevant documents for a given query.

        Args:
            query (str): The query string.

        Returns:
            list[Document]: A list of LangChain Document objects.
        """
        # Perform the search using the semantic search engine
        results = s_store.semantic_search(sc.CD_CONTENT,s_store.get_embedding(query,query_convert=True),MAX_DOCS)
        
        raw_docs = list()
        for item in results:
            obj=dict()
            obj["id"] = item["item"]

            chunk = s_store.corpus.partitions['syllabi-chunked'].chunks[item["item"]]
            obj['title']=chunk.metadata["course_title"]
            obj['number']=chunk.metadata["course_number"]
            obj['instructor']=chunk.metadata["instructor"]
            obj['content']=chunk.get_v_content()
            obj["distance"]=item["distance"]
            raw_docs.append(obj)


        # Convert the search results into LangChain Document objects
        documents = [
            Document(page_content=chunk["content"], id=chunk["id"], metadata={
                "CourseTitle": chunk['title'],
                "CourseNumber": chunk['number'],
                "Instructor": chunk['instructor']
            })
            for chunk in raw_docs
        ]
        # print(f"docs: {documents}")
        return documents

    async def _aget_relevant_documents(self, query: str) -> list[Document]:
        """
        Asynchronous version of get_relevant_documents.

        Args:
            query (str): The query string.

        Returns:
            list[Document]: A list of LangChain Document objects.
        """
        raise NotImplementedError("Async retrieval is not supported for this retriever.")
    
ssr = SyllabusSearchRetriever()

CONFIG = json.load(open("syllabi_config.json"))
API_KEY: str = open("syllabi_concierge").read().strip()
MODEL_NAME: str = "llama3"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
LLAMA3="meta-llama/Llama-3.2-1B"
MISTRAL="mistralai/Mistral-7B-v0.1"

#login(token=API_KEY)

hf_pipeline = HuggingFacePipeline.from_model_id("llama3", task="text-generation",

                                                model_kwargs={"device": 0}, token=API_KEY,

                                                config={"api_token": API_KEY})


qa_chain = RetrievalQA.from_llm(
    hf_pipeline, retriever=ssr
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/c_store")
def get_content():
    return s_store.corpus.get_documents()

@app.get("/doc/{doc_id}")
async def get_document(doc_id: str):
    return s_store.corpus.get_document(doc_id)

@app.get("/find/{word}")
async def find_word(word: str):
    return s_store.find_word_in_content(word)

@app.get("/search/{phrase}/{k}")
async def search_phrase(phrase: str,k: int):
    return s_store.semantic_search(sc.CD_CONTENT,s_store.get_embedding(phrase,query_convert=True),k)

@app.get("/ragify/{query}")
async def ragify(query: str):
    return ssr._get_relevant_documents(query)

@app.get("/infer/{prompt}")
async def infer(prompt: str):
    result = qa_chain.run(prompt)
    return {"answer": result}
