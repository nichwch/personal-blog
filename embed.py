from indexer import Indexer

indexer = Indexer()
updated_files = indexer.get_newly_edited_files()
index_newly_edited_files = indexer.index_newly_edited_files()
indexer.create_file_index_for_new_files()
print(updated_files)





