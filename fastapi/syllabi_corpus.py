import rag_corpus as rgc
from rag_corpus import Corpus, Schema
from transformers import GPT2Tokenizer

import os
import json

CONFIG = json.load(open("syllabi_config.json"))

SYLLABI_DOCS=CONFIG['DOCS_HOME']
KW_INDEX="kw"
CD_CONTENT="content"
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

"""
Leaving this out of the class for now -- we may want to
Define a chunking base interface that would allow us
to swap out different chunking strategies

TODO: Define a Chunker Base class

"""

def chunk_content(content, chunk_size=512, overlap=50):
    """
    Splits text content into fixed-length chunks with overlap.

    Parameters:
    - content: str, the text to be chunked.
    - chunk_size: int, maximum number of tokens per chunk.
    - overlap: int, number of tokens to overlap between chunks.

    Returns:
    - List of text chunks.
    """
    tokens = tokenizer.tokenize(content)
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(tokenizer.convert_tokens_to_string(chunk))

    return chunks            

class SyllabiCorpus(Corpus):

    def __init__(self):
        super().__init__()

        ### Create Schema and Partition
        schema = Schema()
        schema.add_prop("id",str)  # Filename
        schema.add_prop("title",str)
        schema.add_prop("course_title",str)
        schema.add_prop("course_number",str)
        schema.add_prop("instructor",str)
        schema.add_prop("semester",str)
        schema.add_prop("section",str)
        schema.add_prop("download",str) # Link to download pdf (was "link")
        schema.add_prop("page",str) # web page that the syllabus was on (was "parent")

        self.create_partition("syllabi-chunked")
        self.partitions["syllabi-chunked"].schema = schema

        self.create_partition("syllabi-full")
        self.partitions["syllabi-full"].schema = schema

        SYLLABI_FILE = os.path.join(SYLLABI_DOCS, 'syllabi.json')

        SYLLABI = json.load(open(SYLLABI_FILE,'r'))

        for syllabus in SYLLABI:
            if not syllabus["content"]:
                syllabus["content"] = "Error Processing Syllabus"

            filename = syllabus['filename']

            # Set up segment
            self.create_document(filename)
            self.documents[filename].create_segment('content')
            self.documents[filename].segments['content'].set_content(syllabus['content'])

            # Chunk for reverse index 
            chunk_id = f"{filename}.full"
            self.documents[filename].create_chunk("syllabi-full",chunk_id)
            self.documents[filename].chunks[chunk_id].set_property("id",filename)
            self.documents[filename].chunks[chunk_id].set_property("title",syllabus["title"])     
            self.documents[filename].chunks[chunk_id].set_property("course_title",syllabus["course_title"])     
            self.documents[filename].chunks[chunk_id].set_property("course_number",syllabus["course_number"])     
            self.documents[filename].chunks[chunk_id].set_property("instructor",syllabus["instructor"])     
            self.documents[filename].chunks[chunk_id].set_property("semester",syllabus["semester"])     
            self.documents[filename].chunks[chunk_id].set_property("section",syllabus["section"])     
            self.documents[filename].chunks[chunk_id].set_property("download",syllabus["link"])     
            self.documents[filename].chunks[chunk_id].set_property("page",syllabus["parent"])     
            self.documents[filename].chunks[chunk_id].set_i_content(syllabus['content'])     
            self.documents[filename].chunks[chunk_id].set_v_content("")     
            self.documents[filename].chunks[chunk_id].add_segment_id("content")      

            # Chunks for vector store
            chunks = chunk_content(syllabus["content"], chunk_size=512, overlap=50)
            for idx, chunk in enumerate(chunks):
                # Create chunk in partition
                chunk_id = f"{filename}.C{(idx+1):04d}"
                self.documents[filename].create_chunk("syllabi-chunked",chunk_id)
                self.documents[filename].chunks[chunk_id].set_property("id",filename)
                self.documents[filename].chunks[chunk_id].set_property("title",syllabus["title"])     
                self.documents[filename].chunks[chunk_id].set_property("course_title",syllabus["course_title"])     
                self.documents[filename].chunks[chunk_id].set_property("course_number",syllabus["course_number"])     
                self.documents[filename].chunks[chunk_id].set_property("instructor",syllabus["instructor"])     
                self.documents[filename].chunks[chunk_id].set_property("semester",syllabus["semester"])     
                self.documents[filename].chunks[chunk_id].set_property("section",syllabus["section"])     
                self.documents[filename].chunks[chunk_id].set_property("download",syllabus["link"])     
                self.documents[filename].chunks[chunk_id].set_property("page",syllabus["parent"])     
                self.documents[filename].chunks[chunk_id].set_i_content("")     
                self.documents[filename].chunks[chunk_id].set_v_content(chunk)     
                self.documents[filename].chunks[chunk_id].add_segment_id("content")      



