import chromadb
import uuid
from openai import OpenAI
import json
import os
import time
from chromadb import Collection

LAST_INDEXED_TIME = "./config/lastindexeddate.config.txt"
INDEXED_FILES = "./config/indexedfiles.config.json"
POST_DIRECTORY = './posts/'
chroma_client = chromadb.PersistentClient(path="./db")

client = OpenAI()

class Indexer:
    collection: Collection
    last_indexed_date: int
    # neccessary to detect if files have been deleted
    indexed_files: list[str]


    def __init__(self):
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
    
    def get_newly_edited_files(self):
        files_in_post = os.listdir(POST_DIRECTORY)
        files_edited_since_last_index = []
        for post in files_in_post:
            if os.path.getmtime(POST_DIRECTORY + post) > self.last_indexed_date:
                files_edited_since_last_index.append(post)
        return files_edited_since_last_index
    
    def get_embedding(self, content:str):
        res = client.embeddings.create(
                    input=content,
                    model="text-embedding-3-small"
                )
        return res.data[0].embedding
    
    def get_closest_posts(self, query:str):
        embedding = self.get_embedding(query)
        res = self.collection.query(embedding, k=5)
        return res
    
    async def index_file(self, file):
        post_content = open(POST_DIRECTORY + file).read()
        embedding = self.get_embedding(post_content)
        self.collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embedding],
            documents=[post_content],
            metadatas=[{
                'filename':file
            }]
        )
        self.indexed_files.append(file)
        with open(INDEXED_FILES, "w") as file:
            json.dump(self.indexed_files, file)
    
    def index_newly_edited_files(self):
        newly_edited_files = self.get_newly_edited_files() 
        for post in newly_edited_files:
            post_content = open(POST_DIRECTORY + post).read()
            embedding = self.get_embedding(post_content)
            self.collection.add(
                ids=[str(uuid.uuid4())],
                embeddings=[embedding],
                documents=[post_content],
                metadatas=[{
                    'filename':post
                }]
            )
        with open(LAST_INDEXED_TIME, "w") as file:
            file.write(str(time.time()))
        with open(INDEXED_FILES, "w") as file:
            json.dump([], file)
    
    def _debug_log_entries(self):
        breakpoint()


