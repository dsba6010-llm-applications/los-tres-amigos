import numpy as np
import faiss  # Or any other vector store you choose
import json

from whoosh import scoring

from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import QueryParser
from whoosh.query import Or, And, Term

N_DISTANCE="distance"
N_ITEM="item"
N_V_STORE="v_store"
N_XREF="xref"

# Utility Class to store raw embeddings
def get_embeddings_map(raw_embeddings,chunk_ids):
    if len(raw_embeddings) != len (chunk_ids):
        raise Exception("Length of Embeddings and IDs do not match")
    embeddings_map = dict()
    for i in range(len(chunk_ids)):
        embeddings_map[chunk_ids[i]] = raw_embeddings[i]

    return embeddings_map

class RAGStore():
    def __init__(self,corpus=None):
        self.v_stores=dict()
        self.i_indexes=dict()
        self.corpus=corpus

    def distance_xref(self,res,xref):
        (D,I) = res
        results = list()
        for i in range(len(I[0])):
            results.append(dict({
                N_DISTANCE: float(D[0][i]),
                N_ITEM: xref[I[0][i]]
            }))
        return results

    def add_v_store(self,id,v_store,xref):
        self.v_stores[id]={
            N_V_STORE: v_store,
            N_XREF: xref
        }

    def add_i_index(self,id,i_index):
        self.i_indexes[id]=i_index

    def semantic_search(self,id,embedding,k):
        return self.distance_xref(
            self.v_stores[id][N_V_STORE].search(embedding,k),
            self.v_stores[id][N_XREF]
        )
        
    def keyword_search(self,id,query):
        return self.i_indexes[id].search(query)
