from rag_nlp import RAGCachedEmbedder
import numpy as np
from langchain_openai import OpenAIEmbeddings
OPENAI_ROOTNAME="openai-embedding"
class OpenAIEmbedder(RAGCachedEmbedder):
    def __init__(self, model, cache_folder="."):
        self.model=model
        self.cache_filename = f"{OPENAI_ROOTNAME}-{model}.json"
        self.embedding_model = OpenAIEmbeddings(model=model)
        super().__init__(self.cache_filename, cache_folder)

    def get_embedding(self,content,query_convert=False):
        embeddings = self.embedding_model.embed_query(content)

        return np.array(embeddings).astype('float32').reshape(1, -1) if query_convert else embeddings
    
