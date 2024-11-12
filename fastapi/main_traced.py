# main.py

from fastapi import FastAPI, HTTPException
from creative_store import CreativeStore, CD_CONTENT
from tracing import tracer
import logging

# Initialize FastAPI and store
app = FastAPI()
c_store = CreativeStore()

# Set up logging
logger = logging.getLogger(__name__)

@app.get("/")
@tracer.trace_function("root_endpoint")
async def root():
    return {"message": "Hello World"}

@app.get("/find/{word}")
@tracer.trace_function("find_word")
async def find_word(word: str):
    try:
        results = c_store.find_word_in_content(word)
        return results
    except Exception as e:
        logger.error(f"Error finding word {word}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/{phrase}/{k}")
@tracer.trace_function("semantic_search")
async def search_phrase(phrase: str, k: int):
    try:
        # Get embedding for the phrase
        embedding = c_store.get_embedding(phrase, query_convert=True)
        
        # Perform semantic search
        results = c_store.semantic_search(CD_CONTENT, embedding, k)
        
        return results
    except Exception as e:
        logger.error(f"Error in semantic search for {phrase}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)