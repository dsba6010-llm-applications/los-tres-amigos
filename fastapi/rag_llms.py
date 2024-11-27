from langchain_openai.llms.base import OpenAI
from langchain_openai import OpenAIEmbeddings
import json
import requests
import os
CONFIG = json.load(open("llm_config.json"))
openai_api_key = open(f'{CONFIG["KEY_FOLDER"]}/{CONFIG["OPENAI_API_KEY_FILE"]}').read().strip()
os.environ["OPENAI_API_KEY"] = openai_api_key

def get_local_llm():
    return OpenAI(
        base_url=CONFIG["LLM_URL"],
        api_key='ollama',
    )
def get_openai_llm():
    return OpenAI(
       model =  CONFIG["OPEN_AI_MODEL_ID"],
       api_key= openai_api_key
    )

def get_hf_llm():
    hf_api_key = open(f'{CONFIG["KEY_FOLDER"]}/{CONFIG["HF_API_KEY_FILE"]}').read().strip()
    openai_api_key = open(f'{CONFIG["KEY_FOLDER"]}/{CONFIG["OPENAI_API_KEY_FILE"]}').read().strip()
    hf_api_url =  f'https://api-inference.huggingface.co/models/{CONFIG["HF_MODEL_ID"]}'
    os.environ["OPENAI_API_KEY"] = openai_api_key
    class HuggingFaceWrapper(OpenAI):

        def _call(self, prompt):
            headers = {"Authorization": f"Bearer {hf_api_key}"}
            payload = {"inputs": prompt}
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result[0]["generated_text"]  # Adjust based on Hugging Face response structure
            else:
                return f"Error: {response.status_code}"

    return HuggingFaceWrapper(api_key=openai_api_key, base_url = hf_api_url)
def get_local_llm():
    return OpenAI(
        base_url=CONFIG["LLM_URL"],
        api_key='ollama',
    )

LLM_MAPPING = {
    "local": { 
        "llm": get_local_llm,
        "embeddings": get_local_llm(),
        "cache": os.path.join(CONFIG["DOCS_HOME"], CONFIG["LOCAL_DOCS_CACHE"]),
        "model_id": CONFIG["EMBEDDING_MODEL"]
    },
    "hf": {
        "llm": get_hf_llm,
        "embeddings": get_hf_llm(),
        "cache": os.path.join(CONFIG["DOCS_HOME"], CONFIG["HF_DOCS_CACHE"]),
        "model_id": CONFIG["HF_MODEL_ID"]
    },
    "openai": {
        "llm": get_openai_llm,
        "embeddings": OpenAIEmbeddings(model="text-embedding-3-large"),
        "cache": os.path.join(CONFIG["DOCS_HOME"], CONFIG["OPENAI_DOCS_CACHE"]),
        "model_id": CONFIG["OPEN_AI_MODEL_ID"]
    }

    # Add more LLM mappings here as needed
}

def get_llm(name="local"):
    global LLM_MAPPING
    
    # Return the appropriate LLM function result, or raise an error if not found
    if name in LLM_MAPPING:
        return LLM_MAPPING[name]["llm"]()
    else:
        raise ValueError(f"Unknown LLM name: {name}")

def get_cache(name="local"):
    global LLM_MAPPING
    
    # Return the appropriate LLM function result, or raise an error if not found
    if name in LLM_MAPPING:
        return LLM_MAPPING[name]["cache"]
    else:
        raise ValueError(f"Unknown LLM name: {name}")

def get_embeddings(name="local"):
    global LLM_MAPPING
    
    # Return the appropriate LLM function result, or raise an error if not found
    if name in LLM_MAPPING:
        return LLM_MAPPING[name]["embeddings"]
    else:
        raise ValueError(f"Unknown LLM name: {name}")
 
def get_model_id(name="local"):
    global LLM_MAPPING
    
    # Return the appropriate LLM function result, or raise an error if not found
    if name in LLM_MAPPING:
        return LLM_MAPPING[name]["model_id"]
    else:
        raise ValueError(f"Unknown LLM name: {name}")