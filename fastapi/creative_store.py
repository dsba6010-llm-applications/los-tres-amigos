from ragstore import RAGStore
import os
import json

import faiss  # Or any other vector store you choose


from whoosh import scoring

from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import QueryParser
from whoosh.query import Or, And, Term

from openai import OpenAI
import numpy as np
import creative_corpus as cc
#from rag_corpus import Corpus, Partition, Document, Segment, Chunk, Schema
from creative_corpus import CreativeCorpus

CONFIG = json.load(open("config.json"))

client = OpenAI(
    base_url=CONFIG["LLM_URL"],

    # required but ignored
    api_key='ollama',
)


CREATIVE_DOCS=CONFIG["DOCS_HOME"]
KW_INDEX="keyword"
CD_CONTENT="content"
CD_TITLE="title"
class CreativeStore(RAGStore):

    def __init__(self):
        super().__init__(corpus = CreativeCorpus())
        self.index_content()

    def index_content(self):
        schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            content=TEXT(analyzer=StemmingAnalyzer()),
            category=KEYWORD(stored=True, commas=False),
            genre=KEYWORD(stored=True, commas=False)
        )
        storage = RamStorage()
        index = storage.create_index(schema)
        writer = index.writer()

        # Iterate through the documents' chunks in the content partition
        for fileroot in self.corpus.documents:
            writer.add_document(
                id=fileroot,
                title=self.corpus.documents[fileroot].chunks[f"{fileroot}.content"].metadata['title'],
                content=self.corpus.documents[fileroot].chunks[f"{fileroot}.content"].get_i_content(),
                category=self.corpus.documents[fileroot].chunks[f"{fileroot}.content"].metadata['category'],
                genre=self.corpus.documents[fileroot].chunks[f"{fileroot}.content"].metadata['genre']
            )

        writer.commit()
        self.add_i_index(KW_INDEX, index.searcher(weighting=scoring.BM25F()))
        self.embed_content()
    
    def embed_content(self):

        # Embed Content
        raw_embeddings=list()
        fileroots=list()
        for fileroot in self.corpus.documents:
            raw_embeddings.append(self.get_embedding(self.corpus.documents[fileroot].chunks[f"{fileroot}.content"].get_v_content()))
            fileroots.append(f"{fileroot}.content")
            raw_embeddings.append(self.get_embedding(self.corpus.documents[fileroot].chunks[f"{fileroot}.title"].get_v_content()))
            fileroots.append(f"{fileroot}.title")
        
        embeddings = np.array(raw_embeddings).astype('float32')
        dim = embeddings.shape[1]
        vs = faiss.IndexFlatL2(dim)
        vs.add(embeddings)
        self.add_v_store(CD_CONTENT,vs,fileroots)    


    def get_content(self):
        content=dict()
        for doc_id in self.corpus.documents:
            doc = self.corpus.documents[doc_id]
            content[doc_id] = dict()
            content[doc_id]["segments"]=dict()
            for segment_id in doc.segments:
                content[doc_id]["segments"][segment_id] = doc.segments[segment_id].content
            content[doc_id]["chunks"]=dict()
            for chunk_id in doc.chunks:
                content[doc_id]["chunks"][chunk_id] = dict()
                content[doc_id]["chunks"][chunk_id]["partition_id"] = doc.chunks[chunk_id].partition_id
                content[doc_id]["chunks"][chunk_id]["segment_ids"] = list(doc.chunks[chunk_id].segment_ids)
                content[doc_id]["chunks"][chunk_id]["metadata"] = doc.chunks[chunk_id].metadata
                content[doc_id]["chunks"][chunk_id]["i_content"] = doc.chunks[chunk_id].get_i_content()
                content[doc_id]["chunks"][chunk_id]["v_content"] = doc.chunks[chunk_id].get_v_content()
                
            
        return content 

    def find_word_in_content(self, keyword):
        query = QueryParser("content", self.i_indexes[KW_INDEX].schema).parse(keyword)
        results = self.keyword_search(KW_INDEX,query)
        works=list()
        for result in results:
            works.append(result)
        return works
    
    def get_embedding(self,content,query_convert=False):
        embeddings = client.embeddings.create(
            model=CONFIG["EMBEDDING_MODEL"],
            input=content
        )

        return np.array(embeddings.data[0].embedding).astype('float32').reshape(1, -1) if query_convert else embeddings.data[0].embedding