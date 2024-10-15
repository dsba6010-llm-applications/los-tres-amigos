from fastapi import FastAPI
from syllabi_store import SyllabiStore, CD_CONTENT
app = FastAPI()
s_store = SyllabiStore()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/add/{addend1}/{addend2}")
async def add_item(addend1: int,addend2 :int):
    return {"sum": addend1 + addend2}

@app.get("/c_store")
def get_content():
    return s_store.get_content()

@app.get("/doc/{doc_id}")
async def get_content(doc_id: str):
    return s_store.get_document(doc_id)

@app.get("/find/{word}")
async def find_word(word: str):
    return s_store.find_word_in_content(word)

@app.get("/search/{phrase}/{k}")
async def search_phrase(phrase: str,k: int):
    return s_store.semantic_search(CD_CONTENT,s_store.get_embedding(phrase,query_convert=True),k)