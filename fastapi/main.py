from fastapi import FastAPI
from creative_store import CreativeStore
app = FastAPI()
c_store = CreativeStore()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/add/{addend1}/{addend2}")
async def add_item(addend1: int,addend2 :int):
    return {"sum": addend1 + addend2}

@app.get("/c_store")
def get_content():
    return c_store.get_content()

@app.get("/find/{word}")
async def find_word(word: str):
    return c_store.find_word_in_content(word)

@app.get("/embedding/{phrase}")
async def embed_phrase(phrase: str):
    return c_store.get_embedding(phrase)