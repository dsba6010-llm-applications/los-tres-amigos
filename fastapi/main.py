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
import rag_llms as rllm
from openai_embedder import OpenAIEmbedder
from openai_ragifier import SimpleOpenAIRAGifier

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
CONFIG = json.load(open("llm_config.json"))
LLMENV="openai"
openai_api_key = open(f'{CONFIG["KEY_FOLDER"]}/{CONFIG["OPENAI_API_KEY_FILE"]}').read().strip()
os.environ["OPENAI_API_KEY"] = openai_api_key
print(openai_api_key)
sc_llm = rllm.get_llm(LLMENV)
sc_cache = rllm.get_cache(LLMENV)
model_id = rllm.get_model_id(LLMENV)
embeddings=rllm.get_embeddings(LLMENV)

s_store = sc.SyllabiStore(cached_embedder=OpenAIEmbedder("text-embedding-3-large"))
MAX_DOCS=5
logger.info("Store Loaded")
ragifier=SimpleOpenAIRAGifier(s_store,s_store.corpus,s_store.cached_embedder)
## TODO: move to the latest version of OpenAI which uses Pydantic

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
    return ragifier.process_prompt(prompt)
