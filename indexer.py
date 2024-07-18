import chromadb
import uuid
from openai import AsyncOpenAI
import json
import os
import time
from chromadb import Collection
import asyncio

LAST_INDEXED_TIME = "./config/lastindexeddate.config.txt"
INDEXED_FILES = "./config/indexedfiles.config.json"
POST_DIRECTORY = './posts/'
chroma_client = chromadb.PersistentClient(path="./db")

client = AsyncOpenAI()

class Indexer:
    collection: Collection
    last_indexed_date: int
    # neccessary to detect if files have been deleted
    indexed_files: list[str]
    delimiter:str


    def __init__(self, delimiter:str = '\n'):
        try:
            self.collection = chroma_client.get_collection('collection')
        except:
            self.collection = chroma_client.create_collection(name="collection")
        try:
            self.indexed_files = json.load(open(INDEXED_FILES))
        except:
            self.indexed_files = []
        try:
            self.last_indexed_date = int(open(LAST_INDEXED_TIME).read())
        except:
            self.last_indexed_date = 0
        self.delimiter = delimiter
    
    def split_text(self, text:str)->list[str]:
        return text.split(self.delimiter)
    
    def get_newly_edited_files(self):
        files_in_post = os.listdir(POST_DIRECTORY)
        files_edited_since_last_index = []
        for post in files_in_post:
            if os.path.getmtime(POST_DIRECTORY + post) > self.last_indexed_date:
                files_edited_since_last_index.append(post)
        return files_edited_since_last_index
    
    async def get_embedding(self, content:str):
        res = await client.embeddings.create(
                    input=content,
                    model="text-embedding-3-small"
                )
        return res.data[0].embedding
    
    def get_closest_posts(self, query:str):
        embedding = self.get_embedding(query)
        res = self.collection.query(embedding, k=5)
        return res

    # indexes a single segment of a file
    # segments are a file split by self.delimiter
    async def index_segment(self, segment:str, post_name:str) -> list[
        str, list[float], str, dict[str, str]
    ]:
        embedding = await self.get_embedding(segment)
        print('embedded segment of file', post_name)
        print(segment)
        return [str(uuid.uuid4()), embedding, segment, {'filename':post_name}]
    
    # deletes all previous records for this file
    # then indexes all of its segments in parallel
    async def index_file(self, filename:str):
        # TODO: make sure this actually deletes things
        # self.collection.delete(where={'filename':filename})
        post_content = open(POST_DIRECTORY + filename).read()
        segments = self.split_text(post_content)
        results = await asyncio.gather(*[self.index_segment(segment, filename) for segment in segments])
        self.collection.add(
            ids=[result[0] for result in results],
            embeddings=[result[1] for result in results],
            documents=[result[2] for result in results],
            metadatas=[result[3] for result in results]
        )


    
    # gets all newly edited files
    # then indexes them all in parallel
    async def aindex_newly_edited_files(self):
        newly_edited_files = self.get_newly_edited_files() 
        await asyncio.gather(*[self.index_file(file) for file in newly_edited_files])
        with open(LAST_INDEXED_TIME, "w") as file:
            file.write(str(time.time()))
        with open(INDEXED_FILES, "w") as file:
            json.dump([], file)
    def index_newly_edited_files(self):
        asyncio.run(self.aindex_newly_edited_files())

    def _debug_log_entries(self):
        breakpoint()


