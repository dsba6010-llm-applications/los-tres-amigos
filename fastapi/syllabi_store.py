from rag_store import RAGStore
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
import syllabi_corpus as sc
from syllabi_corpus import SyllabiCorpus

CONFIG = json.load(open("syllabi_config.json"))


client = OpenAI(
    base_url=CONFIG["LLM_URL"],

    # required but ignored
    api_key='ollama',
)


SYLLABI_DOCS=CONFIG["DOCS_HOME"]
KW_INDEX="keyword"
CD_CONTENT="content"

class SyllabiStore(RAGStore):

    def __init__(self):
        super().__init__(corpus = SyllabiCorpus())
        self.index_content()