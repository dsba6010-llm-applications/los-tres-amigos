from rag_nlp import RAGIfier, RAGCachedEmbedder
import numpy as np
import json
import os
import rag_corpus as rgc
from rag_corpus import Corpus, Schema
from rag_store import RAGStore
import syllabi_store as sylstr
from openai import OpenAI
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import QueryParser
from whoosh.query import Or, And, Term
import logging
logger = logging.getLogger(__name__)
MAX_DOCS=5
WEIGHT_FACTOR=20 # Divide the hit score by 20
MODEL_ID='gpt-4o-mini'
# Code Advice from https://chatgpt.com/share/6748b4cb-5994-8007-8390-eeaca6cbbeb9
# WHOOSH code advice from https://chatgpt.com/share/6749d486-cb68-8007-b163-281e20e4a9b3
class SimpleOpenAIRAGifier(RAGIfier):
    def __init__(self,store: RAGStore,corpus: Corpus,rag_embedder: RAGCachedEmbedder):
        super().__init__(store,corpus,rag_embedder)
        self.client=OpenAI()

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
        response = self.client.chat.completions.create(
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

        return({
            "answer": response.choices[0].message.content,
            "ragified_prompt": ragified_prompt,
            "full_response": response
        })

class OpenAIRAGifier(RAGIfier):
    def __init__(self,store: RAGStore,corpus: Corpus,rag_embedder: RAGCachedEmbedder):
        super().__init__(store,corpus,rag_embedder)
        self.client=OpenAI()
    
    def analyze_prompt(self,prompt):
        system_prompt = """
            please analyze the user prompt and provide a json object with the following fields (with the exact names speficifed)
            - request: A prompt the conveys what the user is requesting
            - semantic_phrase: The phrase that we will embedded to do a semantic search
            - search_words: A set of words that will be used in keyword search (using or logic)
            - metadata_fields: A set of metadata fields that will be used to filter the results (please make these sub fields and use the exact names only if the prompt indicates that this filtering is necessary -- multuple values will be ORed please always make this a list)
              - instructor: name of the instructor
              - course_number: Course number (just a number without the DSBA)
              - course_title: Title of the course
            if the user prompt implies knowledge a previous prompt produce an empty semantic_phrase, search_words and metadata.
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Or the model of your choice
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        return {
            "retrieval": json.loads(response.choices[0].message.content),
            "prompt": prompt,
            "full_response": response
        }

    def quoted_or_join(self,words):
        phrases=list()
        for word in words:
            phrases.append(f'"{word}"')
        return " OR ".join(phrases)

    def ragify_prompt(self,prompt):
        retrieval = self.analyze_prompt(prompt)["retrieval"]
        if not retrieval["semantic_phrase"]:
            v_results=list()
        else:
            v_results = self.store.semantic_search(sylstr.CD_CONTENT,self.store.cached_embedder.get_embedding(retrieval["semantic_phrase"],query_convert=True),MAX_DOCS)

        logger.info("BUILDING QUERY")
        phrases = retrieval["search_words"]
        query = QueryParser("content", self.store.i_indexes[sylstr.KW_INDEX].schema).parse(self.quoted_or_join(phrases))
        if "metadata_fields" in retrieval and retrieval["metadata_fields"]:
            logger.info(f'need to search on {retrieval["metadata_fields"].keys()}')
            sub_queries=list()
            sub_queries.append(query)
            for field in retrieval["metadata_fields"]:
                if not retrieval["metadata_fields"][field]:
                    continue
                logger.info(f"Adding {field}")
                query = QueryParser(field, self.store.i_indexes[sylstr.KW_INDEX].schema).parse(self.quoted_or_join(retrieval["metadata_fields"][field]))
                sub_queries.append(query)

            query = And(sub_queries)

        logger.info("QUERY BUILT")
        i_results = self.store.keyword_search(sylstr.KW_INDEX,query)
        logger.info(f"QUERY RESULTS: {i_results}")

        raw_docs = list()
        for item in v_results:
            obj=dict()
            obj["id"] = item["item"]

            chunk = self.store.corpus.partitions['syllabi-chunked'].chunks[item["item"]]
            obj['course_title']=chunk.metadata["course_title"]
            obj['course_number']=chunk.metadata["course_number"]
            obj['instructor']=chunk.metadata["instructor"]
            obj['content']=chunk.get_v_content()
            obj["semantic_distance"]=item["distance"]
            obj["v_relevance"] = 1 / (1 + item["distance"])  # Compute relevance score
            obj["relevance"] = 1 / (1 + item["distance"])  # Compute relevance score
            raw_docs.append(obj)

        for hit in i_results:
            obj=dict()
            #logger.info(f"   {hit}")
            obj['id'] = hit['id']

            chunk = self.store.corpus.partitions['syllabi-full'].chunks[f'{hit["id"]}.full']
            obj['course_number'] = hit['course_number']
            obj['course_title'] = hit['course_title']
            obj['instructor'] = hit['instructor']
            obj['content']=chunk.get_i_content()
            obj['hit_score'] = hit.score  # Access the relevance score
            obj["i_relevance"] = hit.score / WEIGHT_FACTOR  # Compute relevance score
            obj["relevance"] = hit.score / WEIGHT_FACTOR  # Compute relevance score
            raw_docs.append(obj)

        
        raw_docs.sort(key=lambda x: x["relevance"], reverse=True)
        ragified_prompt = {
            "system_prompt": """Please use the 'relevant_content' to answer the question posed by the prompt. 
Higher 'relevance' implies greater importance. 
If the prompt implies knowlege from a previous question, it is important that instead of trying to answer the question, you remind the user in a respectul and  
helpful manner that you have no recollection of previous questions and answers. Never try to guess it you do not know the answer""",
            "prompt": prompt,
            "retrieval": retrieval,
            "relevant_content": raw_docs
        }
       
        return ragified_prompt    

    def process_prompt(self,prompt):
        ragified_prompt=self.ragify_prompt(prompt)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Or the model of your choice
            messages=[
                {"role": "system", "content": ragified_prompt["system_prompt"]},
                {"role": "user", "content": ragified_prompt["prompt"]},
                {"role": "assistant", "content": "\n\n".join(
                    f"{doc['course_title']} ({doc['course_number']}), Instructor: {doc['instructor']}: {doc['content']} "
                    f"(Relevance: {doc['relevance']:.2f})"
                    for doc in ragified_prompt["relevant_content"]
                )}
            ]
        )

        return({
            "answer": response.choices[0].message.content,
            "ragified_prompt": ragified_prompt,
            "full_response": response
        })
