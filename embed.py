import chromadb
import json
import os
import time

chroma_client = chromadb.PersistentClient(path="./db")


if(chroma_client.get_collection("collection") is None):
    collection = chroma_client.create_collection(name="collection")
previously_indexed_files = json.load(open('./config/indexedfiles.config.json'))
try:
    last_indexed_date = int(open("./config/lastindexeddate.config.txt").read())
except:
    last_indexed_date = 0

print("Last indexed date: ", last_indexed_date)
files_in_post = os.listdir("./posts")
files_edited_since_last_index = []
# get files edited since last index
for post in files_in_post:
    print(post)
    last_edited = int(os.path.getmtime("./posts/"+post))
    print(last_edited)
    print(last_edited > last_indexed_date)
    if os.path.getmtime("./posts/"+post) > last_indexed_date:
        files_edited_since_last_index.append(post)


write('./config/lastindexeddate.config.txt', str(int(time.time())))
print('files in post')
print(files_in_post)
print('files edited since last index')
print(files_edited_since_last_index)






