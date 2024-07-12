import chromadb
import json
import os
import time

LAST_INDEXED_TIME = "./config/lastindexeddate.config.txt"
INDEXED_FILES = "./config/indexedfiles.config.json"
chroma_client = chromadb.PersistentClient(path="./db")

class Indexer:
    collection: any
    last_indexed_date: int
    previously_indexed_files: list[str]


    def __init__(self):
        if(chroma_client.get_collection("collection") is None):
            self.collection = chroma_client.create_collection(name="collection")
        try:
            self.previously_indexed_files = json.load(open(INDEXED_FILES))
        except:
            self.previously_indexed_files = []
        try:
            self.last_indexed_date = int(open(LAST_INDEXED_TIME).read())
        except:
            self.last_indexed_date = 0
    
    def get_files_edited_since_last_index(self):
        files_in_post = os.listdir("./posts")
        files_edited_since_last_index = []
        for post in files_in_post:
            if os.path.getmtime("./posts/"+post) > self.last_indexed_date:
                files_edited_since_last_index.append(post)
        return files_edited_since_last_index



