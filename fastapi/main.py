from fastapi import FastAPI
import syllabi_store as sc
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s -  %(module)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

app = FastAPI()
logger.info("Loading Store")
s_store = sc.SyllabiStore()
logger.info("Store Loaded")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/add/{addend1}/{addend2}")
async def add_item(addend1: int,addend2 :int):
    return {"sum": addend1 + addend2}

@app.get("/c_store")
def get_content():
    return s_store.corpus.get_content()

@app.get("/doc/{doc_id}")
async def get_document(doc_id: str):
    return s_store.corpus.get_document(doc_id)

@app.get("/find/{word}")
async def find_word(word: str):
    return s_store.find_word_in_content(word)

@app.get("/search/{phrase}/{k}")
async def search_phrase(phrase: str,k: int):
    return s_store.semantic_search(sc.CD_CONTENT,s_store.get_embedding(phrase,query_convert=True),k)