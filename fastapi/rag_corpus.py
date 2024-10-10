import uuid
from collections import OrderedDict
from ordered_set import OrderedSet

# ChatGPT: https://chatgpt.com/share/66fdbcc9-d88c-8007-8c26-b80c451523a0

class InvalidPropertyValueException(Exception):
    def __init__(self,message="Invalid Property Value"):
        super().__init__(message)


class Entity:
    def __init__(self, container, id=None):
        self.id=str(uuid.uuid4()) if id == None else id
        self.container= container
    def __str__(self):
       return id
    def __repr__(self):
        return str(self)

class Property(Entity):
    def __init__(
            self,
            container,
            id :str,
            p_type :type,
            required=False,
            multiple=False):
        super().__init__(container, id)
        self.p_type = p_type
        self.required = required
        self.multiple = multiple
    def __str__(self):
        return f"{self.id}|{self.p_type}|{'multi' if self.multiple else 'single'}"

class Schema:
    def __init__(self):
        self.properties=OrderedDict()

    def add_prop(self,prop_id: str,p_type: type,required = False, multiple=False):
        self.properties[prop_id] = Property(self, prop_id,p_type, required=False, multiple=False)
    def __str__(self):
        return (f"Schema:\n{self.properties}")
    def __repr__(self):
        return str(self)



class Partition(Entity):
    def __init__(self, container, id, schema=Schema()):
        super().__init__(container, id=id)
        self.chunks = OrderedDict()   
        self.schema=schema

    def __str__(self):
       return f"{self.id}\nChunks:\n{self.chunks}\n{self.schema}"
    
class DocEntity(Entity):
    def __init__(self, container, id=None):
        super().__init__(container, id=id)
        self.doc_id = container.id
    def __str__(self):
       return f"{self.id}"
    def __repr__(self):
        return str(self)

class Chunk(DocEntity):
    def __init__(self, container, partition_id, id=None):
        super().__init__(container,id=id)
        self.segment_ids=OrderedSet()
        self.partition_id=partition_id
        self.metadata=dict()
        self.i_content=None
        self.v_content=None
        container.container.partitions[partition_id].chunks[self.id]=self
        

    def add_segment_id(self,segment_id):
        self.segment_ids.add(segment_id)

    def set_i_content(self,content):
        self.i_content = content

    def set_v_content(self,content):
        self.v_content = content

    def set_content(self,content):
        self.set_i_content(content)
        self.set_v_content(content)

    def get_content(self):
        content=None
        for seg_id in self.segment_ids:
            if content == None:
                content = self.container.segments[seg_id].content
            else:
                content += " "
                content += self.container.segments[seg_id].content
        return content

    def get_i_content(self):
        return self.get_content() if self.i_content == None else self.i_content

    def get_v_content(self):
        return self.get_content() if self.v_content == None else self.v_content    

    def set_property(self,id,value):
        schema = self.container.container.partitions[self.partition_id].schema
        if not id in schema.properties:
            raise InvalidPropertyValueException("Invalid Property Name")        
        prop = schema.properties[id]
        if prop.multiple:
            if not isinstance(value,list):
                self.metadata[id]=list()
                self.metadata[id].append(value)
            else:
                self.metadata[id]=value
        else:
            if isinstance(value,list):
                raise InvalidPropertyValueException("Cannot set single value property to a list")
            else:
                self.metadata[id]=value
    
    def add_property(self,id,value):
        if id not in self.metadata:
            self.set_property(id, value)
            return
        schema = self.container.container.partitions[self.partition_id].schema
        if not id in schema.properties:
            raise InvalidPropertyValueException("Invalid Property Name")
        prop = schema.properties[id]
        if not prop.multiple:
            raise InvalidPropertyValueException("Cannot add to single value property")
        if isinstance(value,list):
            self.metadata[id].extend(value)
        else:
            self.metadata[id].append(value)

class Segment(DocEntity):
    def __init__(self,  container,  id=None):
        super().__init__(container,id=id)
        self.content=None
    
    def set_content(self,content):
        self.content=content

class Document(Entity):
    def __init__(self, container, id=None):
        super().__init__(container,id=id)
        self.segments = OrderedDict()
        self.chunks = OrderedDict()

    def create_segment(self, id=None):
        segment = Segment(self, id)
        self.segments[segment.id]=segment
        return segment.id

    def create_chunk(self, partition_id, id=None):
        chunk = Chunk(self, partition_id, id)
        self.chunks[chunk.id]=chunk
        return chunk.id
    
    def __str__(self):
       return f"{self.id}\nChunks:\n{self.chunks}\Segments:\n{self.segments}"

class Corpus:
    def __init__(self):
        self.documents=OrderedDict()
        self.partitions=OrderedDict()
    
    def __str__(self):
        return f"Corpus:\Partitions:\n{self.partitions}\nDocuments:\n{self.documents}"
    
    def __repr__(self):
        return str(self)


    def create_document(self, id=None):
        doc = Document(self,id)
        self.documents[doc.id]=doc
        return doc.id

    def create_partition(self, id):
        partition = Partition(self,id)
        self.partitions[partition.id]=partition
        return partition.id
