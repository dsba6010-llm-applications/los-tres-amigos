from rag_store import RAGStore
import rag_store as rs
import os
import json
import logging

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


KW_INDEX="keyword"
CD_CONTENT="content"


logger = logging.getLogger(__name__)

class SyllabiStore(RAGStore):

    def __init__(self,cached_embedder):
        super().__init__(corpus = SyllabiCorpus())
        self.cached_embedder = cached_embedder
        self.load_content()
    
    def load_content(self):
        logger.info("Indexing Content")
        self.index_content()
        logger.info("Embedding Content")
        self.embed_content()
        logger.info("READY")

    def index_content(self):
        schema = Schema(
            id=ID(stored=True, unique=True),
            course_title=TEXT(stored=True),
            content=TEXT(analyzer=StemmingAnalyzer()),
            course_number=KEYWORD(stored=True, commas=False),
            semester=TEXT(stored=True),
            instructor=TEXT(stored=True)
        )
        storage = RamStorage()
        index = storage.create_index(schema)
        writer = index.writer()

        # Iterate through the documents' chunks in the content partition
        for filename in self.corpus.documents:
            chunk_id = f"{filename}.full"
            writer.add_document(
                id=filename,
                course_title=self.corpus.documents[filename].chunks[chunk_id].metadata['course_title'],
                content=self.corpus.documents[filename].chunks[chunk_id].get_i_content(),
                course_number=self.corpus.documents[filename].chunks[chunk_id].metadata['course_number'],
                semester=self.corpus.documents[filename].chunks[chunk_id].metadata['semester'],
                instructor=self.corpus.documents[filename].chunks[chunk_id].metadata['instructor']
            )

        writer.commit()
        self.add_i_index(KW_INDEX, index.searcher(weighting=scoring.BM25F()))


    def embed_content(self):

        # Embed Content
        existing_embeddings=self.cached_embedder.load_embeddings_cache()
        raw_embeddings=list()
        filenames=list()
        file_no=0
        for filename in self.corpus.documents:
            file_no += 1
            logger.info(f"FILE {file_no}: {filename}")
            for chunk_id in self.corpus.documents[filename].chunks:
                if self.corpus.documents[filename].chunks[chunk_id].partition_id != "syllabi-chunked":
                    continue
                logger.info(f"  CHUNK: {chunk_id}")
                if chunk_id in existing_embeddings:
                    raw_embeddings.append(existing_embeddings[chunk_id])
                else:
                    raw_embeddings.append(
                        self.cached_embedder.get_embedding(self.corpus.documents[filename].chunks[chunk_id].get_v_content())
                    )
                filenames.append(chunk_id)

        self.cached_embedder.store_embeddings_cache(rs.get_embeddings_map(raw_embeddings,filenames))
        embeddings = np.array(raw_embeddings).astype('float32')
        dim = embeddings.shape[1]
        vs = faiss.IndexFlatL2(dim)
        vs.add(embeddings)
        self.add_v_store(CD_CONTENT,vs,filenames)
        

    def find_word_in_content(self, keyword):
        query = QueryParser("content", self.i_indexes[KW_INDEX].schema).parse(keyword)
        results = self.keyword_search(KW_INDEX,query)
        works=list()
        for result in results:
            works.append(result)
        return works
    