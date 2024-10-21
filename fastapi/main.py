from fastapi import FastAPI
from creative_store import CreativeStore, CD_CONTENT
app = FastAPI()
c_store = CreativeStore()
from fastapi import FastAPI
from routes import router  # Assuming routes.py is in the same directory as main.py

# Create a FastAPI application instance with a title
app = FastAPI(title="UNC Charlotte Chatbot")

# Include the router, which contains our API endpoints
app.include_router(router)

# This block allows us to run the app directly with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


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

@app.get("/search/{phrase}/{k}")
async def search_phrase(phrase: str,k: int):
    return c_store.semantic_search(CD_CONTENT,c_store.get_embedding(phrase,query_convert=True),k)