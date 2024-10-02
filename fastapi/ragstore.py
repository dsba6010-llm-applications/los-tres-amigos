import numpy as np
import faiss  # Or any other vector store you choose


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

class RAGStore():
    def __init__(self):
        self.v_stores=dict()
        self.i_indexes=dict()

    def distance_xref(self,res,xref):
        (D,I) = res
        results = list()
        for i in range(len(I[0])):
            results.append(dict({
                N_DISTANCE: D[0][i],
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
