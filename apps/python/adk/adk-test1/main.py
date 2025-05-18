# from .agent import store_embeddings_in_milvus, load_and_process_documents
import os
from langchain.document_loaders import TextLoader  # Example loader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from dotenv import load_dotenv

load_dotenv()
MILVUS_HOST = os.environ.get("MILVUS_HOST", "localhost")
MILVUS_PORT = os.environ.get("MILVUS_PORT", "19530")
MILVUS_COLLECTION_NAME="my_rag_collection"
EMBEDDING_MODEL_NAME="all-mpnet-base-v2"
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
connections.connect(alias="default", host="localhost", port="19530")
print(utility.list_collections())
def load_and_process_documents(file_path: str):
  """Loads and splits documents."""
  loader = TextLoader(file_path)
  documents = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
  chunks = text_splitter.split_documents(documents)
  return chunks

def create_milvus_collection():
  """Creates the Milvus collection if it doesn't exist."""
  if not utility.has_collection(MILVUS_COLLECTION_NAME):
    fields = [
      FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
      FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR,
                  dim=embedding_model.get_sentence_embedding_dimension()),
      FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
      FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
    ]
    schema = CollectionSchema(fields=fields, description="RAG collection")
    collection = Collection(MILVUS_COLLECTION_NAME, schema=schema)
    index_params = {
      "metric_type": "COSINE",
      "index_type": "IVF_FLAT",
      "params": {"nlist": 128},
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    collection.load()
    return collection
  else:
    collection = Collection(MILVUS_COLLECTION_NAME)
    collection.load()
    return collection


def store_embeddings_in_milvus(documents):
  """Generates embeddings and stores them in Milvus."""
  collection = create_milvus_collection()
  embeddings = embedding_model.encode([doc.page_content for doc in documents])
  data = [
    embeddings,
    [doc.page_content for doc in documents],
    [doc.metadata["source"] for doc in documents],
  ]
  collection.insert(data)
  collection.flush()
  return collection.num_entities


def main():
  print("Hello from agent2!")
  file_path = "my_knowledge.txt"
  if os.path.exists(file_path):
    documents = load_and_process_documents(file_path)
    num_entities = store_embeddings_in_milvus(documents)
    print(f"Indexed {num_entities} document chunks in Milvus.")
  else:
    print(f"Please create a file named '{file_path}' with your knowledge.")


if __name__ == "__main__":
  main()
