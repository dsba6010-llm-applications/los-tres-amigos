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

CONFIG = json.load(open("config.json"))

client = OpenAI(
    base_url=CONFIG["LLM_URL"],

    # required but ignored
    api_key='ollama',
)


CREATIVE_DOCS=CONFIG["DOCS_HOME"]
KW_INDEX="kw"
CD_CONTENT="content"
class CreativeStore(RAGStore):

    def __init__(self):
        super().__init__()
        LYRICS_INDEX_FILE = IMAGE_FOLDER = os.path.join(CREATIVE_DOCS, 'lyrics.json')
        LYRICS_FACETS_FILE = IMAGE_FOLDER = os.path.join(CREATIVE_DOCS, 'lyrics_facets.json')
        LYRICS_INDEX = json.load(open(LYRICS_INDEX_FILE,'r'))
        LYRICS_FACETS = json.load(open(LYRICS_FACETS_FILE,'r'))
        CONTENT = dict()
        for title, fileroot in LYRICS_INDEX.items():
            CONTENT[fileroot] = {
                'title': title,
                'content': open(os.path.join(CREATIVE_DOCS,f"{fileroot}.txt"),'r').read()
            }
        for fileroot in LYRICS_FACETS:
            CONTENT[fileroot]['category'] = LYRICS_FACETS[fileroot]['category']
            CONTENT[fileroot]['genre'] = LYRICS_FACETS[fileroot]['genre']
        self.content = CONTENT
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

        for fileroot in self.content:
            writer.add_document(
                id=fileroot,
                title=self.content[fileroot]['title'],
                content=self.content[fileroot]['content'],
                category=self.content[fileroot]['category'],
                genre=self.content[fileroot]['genre']
            )

        writer.commit()
        self.add_i_index("kw", index.searcher(weighting=scoring.BM25F()))
        self.embed_content()
    
    def embed_content(self):

        raw_embeddings=list()
        fileroots=list()
        for fileroot in self.content:
            raw_embeddings.append(self.get_embedding(self.content[fileroot]['content']))
            fileroots.append(fileroot)
        
        embeddings = np.array(raw_embeddings).astype('float32')
        dim = embeddings.shape[1]
        vs = faiss.IndexFlatL2(dim)
        vs.add(embeddings)
        self.add_v_store(CD_CONTENT,vs,fileroots)    


    def get_content(self):
        return self.content

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