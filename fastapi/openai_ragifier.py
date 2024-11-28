from rag_nlp import RAGIfier, RAGCachedEmbedder
import numpy as np
import json
import os
import rag_corpus as rgc
from rag_corpus import Corpus, Schema
from rag_store import RAGStore
import syllabi_store as sylstr
import openai
MAX_DOCS=5
MODEL_ID='gpt-4o-mini'
# Code Advice from https://chatgpt.com/share/6748b4cb-5994-8007-8390-eeaca6cbbeb9
class SimpleOpenAIRAGifier(RAGIfier):
    def __init__(self,store: RAGStore,corpus: Corpus,rag_embedder: RAGCachedEmbedder):
        super().__init__(store,corpus,rag_embedder)

    def ragify_prompt(self,prompt):
        results = self.store.semantic_search(sylstr.CD_CONTENT,self.store.cached_embedder.get_embedding(prompt,query_convert=True),MAX_DOCS)
        
        raw_docs = list()
        for item in results:
            obj=dict()
            obj["id"] = item["item"]

            chunk = self.store.corpus.partitions['syllabi-chunked'].chunks[item["item"]]
            obj['course_title']=chunk.metadata["course_title"]
            obj['course_number']=chunk.metadata["course_number"]
            obj['instructor']=chunk.metadata["instructor"]
            obj['content']=chunk.get_v_content()
            obj["semantic_distance"]=item["distance"]
            obj["relevance"] = 1 / (1 + item["distance"])  # Compute relevance score
            raw_docs.append(obj)

        raw_docs.sort(key=lambda x: x["relevance"], reverse=True)
        ragified_prompt = {
            "system_prompt": "Please use the 'relevant_content' to respond to the prompt. Higher 'relevance' implies greater importance. Semantic distance is inversely proportional to relevance.",
            "prompt": prompt,
            "relevant_content": raw_docs
        }
       
        return ragified_prompt    

    def process_prompt(self,prompt):
        ragified_prompt=self.ragify_prompt(prompt)
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Or the model of your choice
            messages=[
                {"role": "system", "content": ragified_prompt["system_prompt"]},
                {"role": "user", "content": ragified_prompt["prompt"]},
                {"role": "assistant", "content": "\n\n".join(
                    f"{doc['course_title']} ({doc['course_number']}), Instructor: {doc['instructor']}: {doc['content']} "
                    f"(Semantic Distance: {doc['semantic_distance']}, Relevance: {doc['relevance']:.2f})"
                    for doc in ragified_prompt["relevant_content"]
                )}
            ]
        )
        return(response)
