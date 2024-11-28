import json
import os
import rag_corpus as rgc
from rag_corpus import Corpus, Schema
from rag_store import RAGStore
class RAGCachedEmbedder():
    def __init__(self,cache_filename,cache_folder="."):
        self.cache_path=os.path.join(cache_folder,cache_filename)

    def get_embedding(self,content,query_convert=False):
        raise NotImplementedError("Get Embedding Unimplelemted Method")

    def update_embeddings_cache(self,embeddings_map):
        existing_map = self.load_embeddings_cache()
        existing_map.update(embeddings_map)
        self.store_embeddings_cache(existing_map)

    def load_embeddings_cache(self):
        try:
            return json.load(open(self.cache_path)) # TODO:handle nocache
        except Exception:
            return dict()

    def store_embeddings_cache(self,embeddings_map):
        json.dump(embeddings_map,open(self.cache_path,"w"))

    
class RAGIfier():
    def __init__(self,store: RAGStore,corpus: Corpus,rag_embedder: RAGCachedEmbedder):
        self.rag_embedder = rag_embedder
        self.corpus = corpus
        self.store = store

    def ragify_prompt(self,prompt):
        raise NotImplementedError("Get Embedding Unimplelemted Method")       

    def process_prompt(self,prompt):
        raise NotImplementedError("Get Embedding Unimplelemted Method")       

