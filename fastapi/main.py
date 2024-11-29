from fastapi import FastAPI
import syllabi_store as sc
import logging
import os
from openai_embedder import OpenAIEmbedder
from openai_ragifier import OpenAIRAGifier
import json
from copy import deepcopy
os.environ['KMP_DUPLICATE_LIB_OK']='True'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s -  %(module)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()
logger.info("Loading Store")

# Load Global Config
CONFIG = json.load(open("llm_config.json"))
openai_api_key = open(f'{CONFIG["KEY_FOLDER"]}/{CONFIG["OPENAI_API_KEY_FILE"]}').read().strip()
os.environ["OPENAI_API_KEY"] = openai_api_key

## Load Syllabus Store
s_store = sc.SyllabiStore(cached_embedder=OpenAIEmbedder("text-embedding-3-large"))
logger.info("Store Loaded")

## Set Up Ragifier
ragifier=OpenAIRAGifier(s_store,s_store.corpus,s_store.cached_embedder)

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
    return ragifier.ragify_prompt(query)

@app.get("/analyze/{query}")
async def ragify(query: str):
    return ragifier.analyze_prompt(query)

@app.get("/infer/{prompt}")
async def infer(prompt: str, verbose: bool = False):
    result =  ragifier.process_prompt(prompt)
    if verbose:
        return result
    else:
        summary = {
            "answer": result["answer"],
            "ragified_prompt": {
                "prompt": result["ragified_prompt"]["prompt"], 
                "retrieval": result["ragified_prompt"]["retrieval"],
                "relevant_content": list()
            },
            "full_response": result["full_response"]
            
        }
        for doc in result["ragified_prompt"]["relevant_content"]:
            obj = deepcopy(doc)
            del(obj["content"])
            summary["ragified_prompt"]["relevant_content"].append(obj)
        return summary

