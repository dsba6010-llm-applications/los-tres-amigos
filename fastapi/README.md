# Chatbot Backend API

## Components

### FastAPI REST Endpoint

This is a work in progress that has a demo based upon an early implementation of the CreativeStore.

We are working on providing a RAGStore and RAGCorpus set of base classes to support the createion of Application Specific RAG Stores and Corpora



###  RAG Store

The RAG Store is a structure that contains a collection of inverted indexes and vector stores.  Support for multiple indexes and vector stores gives us the ability to fine tune RAG Store to support a myriad of use cases.

The RAG Store is a base class.  An application would have a derived class extending the RAG Store.

We have a placeholder corpus field.  An application specific RAG Store would be associated with a corpus that matched the use case.  The application specific RAG Store would be designed to properly populate the vector stores and inverted indexes.

Additionally it would provide appropriate access methods to support the types of search needed for the application

### RAG Corpus

The RAG Corpus is a structure that allows us to load the documents from an arbitrary source of documents. The current recommended use pattern
is to create a derived class to handle the population of the corpus.

The corpus is made up of a collection of Documents and Partions

#### Documents

Documents are made up of Segments (Parts of the dociunments) and Chunks

Segments are non-overlapping portions of the Document.

Chunks are portions of the documents that are added to the RAG Store.  Chunks can reference one or more segments (content outside of the chunk might be useful for context)

#### Partitions are groupings of Chunks

Each Chunk is part of a partiton.  The partition defines how the chunks are indexed in the inverted index and how they are embedded in the vector store.

The partion has a schema associated with it that defines the properties that will be included in the inverted index. These properties can be used for faceted search and filtering.
