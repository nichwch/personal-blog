from indexer import Indexer

indexer = Indexer()
updated_files = indexer.get_newly_edited_files()
index_newly_edited_files = indexer.index_newly_edited_files()
# indexer.create_index()
indexer._debug_log_entries()
print(updated_files)





