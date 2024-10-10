import rag_corpus as rgc
from rag_corpus import Corpus, Partition, Document, Segment, Chunk, Schema

import os
import json

CONFIG = json.load(open("config.json"))

CREATIVE_DOCS=CONFIG["DOCS_HOME"]
KW_INDEX="kw"
CD_CONTENT="content"

class CreativeCorpus(Corpus):
    def __init__(self):
        super().__init__()

        ### Create Schema
        schema = Schema()
        schema.add_prop("id",str)
        schema.add_prop("title",str)
        schema.add_prop("category",str)
        schema.add_prop("genre",str)
        self.create_partition("songs")
        self.partitions["songs"].schema = schema

        tschema = Schema()
        tschema.add_prop("id",str)
        tschema.add_prop("category",str)
        tschema.add_prop("genre",str)
        self.create_partition("titles")
        self.partitions["titles"].schema = tschema

        ### Create the Partitions

        LYRICS_INDEX_FILE = os.path.join(CREATIVE_DOCS, 'lyrics.json')
        LYRICS_FACETS_FILE =  os.path.join(CREATIVE_DOCS, 'lyrics_facets.json')
        LYRICS_INDEX = json.load(open(LYRICS_INDEX_FILE,'r'))
        LYRICS_FACETS = json.load(open(LYRICS_FACETS_FILE,'r'))

        for title, fileroot in LYRICS_INDEX.items():
            self.create_document(fileroot)
            self.documents[fileroot].create_segment('title')
            self.documents[fileroot].segments['title'].set_content(title)
            self.documents[fileroot].create_segment('content')
            self.documents[fileroot].segments['content'].set_content(
                open(os.path.join(CREATIVE_DOCS,f"{fileroot}.txt"),'r').read()
            )

            self.documents[fileroot].create_chunk("titles",f"{fileroot}.title")
            self.documents[fileroot].chunks[f"{fileroot}.title"].set_property("category",LYRICS_FACETS[fileroot]['category'])
            self.documents[fileroot].chunks[f"{fileroot}.title"].set_property("genre",LYRICS_FACETS[fileroot]['genre'])     
            self.documents[fileroot].chunks[f"{fileroot}.title"].add_segment_id("title")      

            self.documents[fileroot].create_chunk("songs",f"{fileroot}.content")
            self.documents[fileroot].chunks[f"{fileroot}.content"].set_property("category",LYRICS_FACETS[fileroot]['category'])
            self.documents[fileroot].chunks[f"{fileroot}.content"].set_property("genre",LYRICS_FACETS[fileroot]['genre'])     
            self.documents[fileroot].chunks[f"{fileroot}.content"].set_property("title",title)     
            self.documents[fileroot].chunks[f"{fileroot}.content"].add_segment_id("content")      

