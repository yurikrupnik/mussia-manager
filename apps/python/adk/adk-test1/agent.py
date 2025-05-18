import datetime
# from turtledemo.sorting_animate import instructions1
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from .util import load_instruction_from_file
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from sentence_transformers import SentenceTransformer
from langchain.document_loaders import TextLoader  # Example loader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


shit_agent = Agent(
    name="stam_agent",
    # model="gemini-2.0-flash",
    model="openai/gpt-3.5-turbo",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    # instruction=load_instruction_from_file("shorts_agent+instruction.txt"),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)

from tavily import TavilyClient
import os
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def search_web(query: str) -> dict:
  """Searches the web using Tavily for the given query.

  Args:
      query (str): The search query.

  Returns:
      dict: A dictionary containing the search results or an error message.
  """
  if not TAVILY_API_KEY:
    return {
      "status": "error",
      "error_message": "Tavily API key not found in environment variables.",
    }
  try:
    search_results = tavily_client.search(query=query, max_results=3)
    return {"status": "success", "results": search_results.get("results", [])}
  except Exception as e:
    return {"status": "error", "error_message": str(e)}

MILVUS_HOST = os.environ.get("MILVUS_HOST", "localhost")
MILVUS_PORT = os.environ.get("MILVUS_PORT", "19530")
MILVUS_COLLECTION_NAME="my_rag_collection"
EMBEDDING_MODEL_NAME="all-mpnet-base-v2"

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
# Connect to Milvus
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)


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


def retrieve_relevant_documents(query: str, top_k: int = 3):
  """Retrieves relevant documents from Milvus based on the query."""
  collection = Collection(MILVUS_COLLECTION_NAME)
  query_embedding = embedding_model.encode([query])[0].tolist()
  search_params = {
    "metric_type": "COSINE",
    "params": {"nprobe": 16},
  }
  results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param=search_params,
    limit=top_k,
    expr=None,  # You can add filters here if needed
    output_fields=["content", "source"],
  )
  retrieved_docs = []
  for hits in results:
    for hit in hits:
      retrieved_docs.append(
        {"content": hit.entity.get("content"), "source": hit.entity.get("source"), "score": hit.distance})
  return retrieved_docs


def rag_tool(query: str) -> dict:
  """Retrieves relevant documents based on the query."""
  relevant_docs = retrieve_relevant_documents(query)
  if relevant_docs:
    context = "\n\n".join([doc["content"] for doc in relevant_docs])
    return {
      "status": "success",
      "context": context,
      "sources": [doc["source"] for doc in relevant_docs],
    }
  else:
    return {"status": "success", "context": "No relevant documents found."}


root_agent = LlmAgent(
    name="weather_time_agent",
    # model="gemini-2.0-flash",
    model=LiteLlm(model="openai/gpt-4o"),  # LiteLLM model string format
    # model=LiteLlm(model="ollama_chat/gemma2"),
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=load_instruction_from_file("instruction.txt"),
    # instruction=(
    #     "You are a helpful agent who can answer user questions about the time and weather in a city."
    # ),
    tools=[get_weather, get_current_time, search_web, rag_tool],
)
