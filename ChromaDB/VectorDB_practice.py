import chromadb
from  embeddings import embed_texts

# 1. Instantiate a client

persist_directory = "./chroma_persist"
client = chromadb.PersistentClient(path=persist_directory)

print("##########Step1 Instantiate a client✅#############")

#2. create databases

my_db_collection_name = "my_demo_collection"

existing_collections = [c.name for c in client.list_collections()]

if my_db_collection_name in existing_collections:
    print(f"Collection '{my_db_collection_name}' already exists.")
    my_db_collection = client.get_collection(name=my_db_collection_name)
else:
    print(f"Collection '{my_db_collection_name}' not found. Creating it now...")
    my_db_collection = client.create_collection(name=my_db_collection_name)
    print(f"Collection '{my_db_collection_name}' created successfully.")

# Show all collections to confirm
print("Current collections:", [c.name for c in client.list_collections()])

print("##########Step2 find or create the collection✅#############")



#3. load documents, embeded

#sample docs
docs = [
    "Chroma is an open-source vector database.",
    "Vector databases store embeddings used by semantic search.",
    "SentenceTransformers provide local embedding models like all-MiniLM-L6-v2.",
    "You can combine Chroma with retrieval augmented generation (RAG).",
    "Al Maaref University has the following university major specializations: Computer Science, Engineering, Media, Religious Studies, and Health Sciences."
]

#create list of id for each document
ids = [f"doc{i}" for i in range(len(docs))]

metadatas = [
    {"source": "lecture", "topic": "chroma"},
    {"source": "book", "topic": "vector-db"},
    {"source": "book", "topic": "embeddings"},
    {"source": "video", "topic": "RAG"},
    {"source": "website", "topic": "University"},
]

# compute embeddings (list of np arrays)
vectors = embed_texts(docs)

print("##########Step3 loading and embedding the documents✅#############")


#4 Add the data(ids, text, metadata and embeding vector in the collection)
#upsert() = update if exists, insert if not
my_db_collection.upsert(  
    ids=ids,
    documents=docs,
    metadatas=metadatas,
    embeddings=vectors
)

#add() = insert only, will cause duplication or errors if IDs already exist
#Upsert into the collection (creates or replaces by id)
#upsert() = update if exists, insert if not

#my_db_collection.add(
#    ids=ids,
#    documents=docs,
#    metadatas=metadatas,
#    embeddings=vectors
#)
print("Inserted", len(ids), "documents into collection:", my_db_collection.name)
print("##########Step4 Adding into the collection✅#############")

#5. Check collection contents

print("Collection size:", my_db_collection.count())
data = my_db_collection.peek(limit=3)
#peek: shows a sample (default 10) of the stored documents, including:
#IDs, Documents, Metadata, and Embeddings (if available)
print("----- data inside using Peek----:\n", data)

# fetch specific doc by id:
result = my_db_collection.get(ids=["doc2"], include=["documents", "metadatas", "embeddings"])
print("---- doc2 using get function----\n:", result)

# get documents using where statement and filter
results = my_db_collection.get(where={"source":"book"})
print("---- get by filter ----:\n")
for i, doc_id in enumerate(results["ids"]):
    print(f"\nID: {doc_id}")
    print("Metadata:", results["metadatas"][i])
    print("Text:", results["documents"][i])

print("##########Step5 check the collection✅#############")

#6. Update a document
# update metadata for a doc based on document ID
# you can update existing document, metadata, or embeddings
my_db_collection.update(
    ids=["doc2"],
    metadatas=[{"source":"lab-notes", "topic":"embeddings", "level":"intro"}]
)

# verify metadata updated
print("--- newly updated doc2 ----:\n", my_db_collection.get(ids=["doc2"], include=["metadatas"]))
print("##########Step6 update the collection✅#############")




#7. Semantic Search
print("\nSemantic Search")
query = "Suggest to me university specializations to apply for"
print(f"Query: {query}")
q_vec = embed_texts([query])[0]  # single embedding vector

results = my_db_collection.query(
    #query_texts=[query],
    query_embeddings=[q_vec],
    n_results=3,
    include=["documents", "metadatas", "distances"]
)
print("\n\n-------Semantic Search Result --------\n", results)
# Access results properly
print("---- Semantic Search Results ----\n")

for i, doc_id in enumerate(results["ids"][0]):  # note [0] because Chroma returns nested lists
    print(f"\nResult {i+1}:")
    print("ID:", doc_id)
    print("Metadata:", results["metadatas"][0][i])
    print("Text:", results["documents"][0][i])

print("##########Step7 Semantic Search✅#############")


#8. delete a document
# delete specific document(s)
my_db_collection.delete(ids=["doc0"])
print("After deletion, size: ", my_db_collection.count())

# delete by filter (for example delete all documents where metadata.topic == 'RAG')
my_db_collection.delete(where={"topic": "RAG"})   # some clients accept 'where' syntax; otherwise fetch ids and delete by id list.

# drop (delete) the whole collection
client.delete_collection(name=my_db_collection_name)
print("Collections after delete: ", [c.name for c in client.list_collections()])
print("##########Step8 Deleting✅#############")


