import chromadb
import uuid
from openai import AsyncOpenAI, OpenAI
import json
import os
import time
from chromadb import Collection
import asyncio

LAST_INDEXED_TIME = "./config/lastindexeddate.config.txt"
INDEXED_FILES = "./config/indexedfiles.config.json"
POST_DIRECTORY = './posts/'
chroma_client = chromadb.PersistentClient(path="./db")

async_client = AsyncOpenAI()
client = OpenAI()


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
            self.collection = chroma_client.create_collection(name="collection", metadata={"hnsw:space": "cosine"})
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
                print(self.last_indexed_date,',',os.path.getmtime(POST_DIRECTORY + post))
                files_edited_since_last_index.append(post)
        return files_edited_since_last_index
    
    async def get_embedding(self, content:str):
        res = await async_client.embeddings.create(
                    input=content,
                    model="text-embedding-3-small"
                )
        return res.data[0].embedding
    
    def get_closest_posts(self, query:str):
        embedding = client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        ).data[0].embedding
        res = self.collection.query(embedding, n_results=10)
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
        post_content = open(POST_DIRECTORY + filename).read()
        segments = self.split_text(post_content)
        segments = [segment for segment in segments if segment != '' and not segment.startswith('//')]
        results = await asyncio.gather(*[self.index_segment(segment, filename) for segment in segments])
        return results

    # gets all newly edited files
    # then indexes them all in parallel
    async def aindex_newly_edited_files(self):
        newly_edited_files = self.get_newly_edited_files() 
        results = await asyncio.gather(*[self.index_file(file) for file in newly_edited_files])
        for segments in results:
            print(segments[0][3])
            filename = segments[0][3]['filename']
            print('inserting to db for:', filename)
            self.collection.delete(where={'filename':{'$eq':filename}})
            self.collection.add(
                ids=[segment[0] for segment in segments],
                embeddings=[segment[1] for segment in segments],
                documents=[segment[2] for segment in segments],
                metadatas=[segment[3] for segment in segments]
            )
            print('successfully inserted to db for:', filename)


    def index_newly_edited_files(self):
        asyncio.run(self.aindex_newly_edited_files())
        print('event loop closed!')
        print('time:',time.time())
        with open(LAST_INDEXED_TIME, "w") as file:
            file.write(str(time.time()))
        with open(INDEXED_FILES, "w") as file:
            json.dump([], file)
    
    def create_file_index(self, file:str):
        file_text = open(POST_DIRECTORY + file).read()
        segments = self.split_text(file_text)
        results = {}
        print('creating index for ',file)
        for segment in segments:
            matches = self.get_closest_posts(segment)
            matchObjs = []
            for i in range(10):
                content = matches['documents'][0][i]
                parent = matches['metadatas'][0][i]['filename']
                score = matches['distances'][0][i]
                matchObjs.append({'content':content, 'parent':parent, 'score':score})
            results[segment] = matchObjs
        return results

    def create_file_index_for_new_files(self):
        files = self.get_newly_edited_files()
        origin_files = set()
        for file in files:
            file_name = file.split('.')[0]
            res = self.create_file_index(file)
            for key in res.keys():
                for match in res[key]:
                    parent = match['parent']
                    print(parent)
                    origin_files.add(parent)
            with open(f'./post-index-test/posts--{file_name}.json', "x") as file:
                file.write(json.dumps(res))
        print(origin_files)

    def create_index(self):
        files = os.listdir(POST_DIRECTORY)
        for file in files:
            file_name = file.split('.')[0]
            res = self.create_file_index(file_name)
            with open(f'./post-index-test/posts--{file_name}.json', "w") as file:
                file.write(json.dumps(res))

    def _debug_log_entries(self):
        breakpoint()


