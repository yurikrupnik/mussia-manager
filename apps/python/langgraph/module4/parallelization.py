from mylibrary import initialize_environment, add, multiply, divide
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage, SystemMessage
from typing_extensions import TypedDict
from typing import Literal, Any, Self
import random
from dataclasses import dataclass
from pydantic import BaseModel, field_validator, ValidationError
from operator import add
from langgraph.checkpoint.memory import MemorySaver
from typing import List, Optional, Annotated
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI

initialize_environment()

llm = ChatOpenAI(model="gpt-4o")
# llm = ChatOllama(model="llama3.1")  # or llama2, codellama, etc.

class State(TypedDict):
  question: str
  answer: str
  context: Annotated[list, add]

# class ReturnNodeValue:
#   def __init__(self, node_secret: str):
#     self._value = node_secret
#
#   def __call__(self, state: State):
#     print(f"Adding {self._value} to {state['state']}")
#     return {"state": [self._value]}

def search_web(state):
  """ Retrieve docs from web search """

  # Search
  tavily_search = TavilySearchResults(max_results=3)
  search_docs = tavily_search.invoke(state['question'])

  # Format
  formatted_search_docs = "\n\n---\n\n".join(
    [
      f'<Document href="{doc["url"]}">\n{doc["content"]}\n</Document>'
      for doc in search_docs
    ]
  )

  return {"context": [formatted_search_docs]}


def search_wikipedia(state):
  """ Retrieve docs from wikipedia """

  # Search
  search_docs = WikipediaLoader(query=state['question'],
                                load_max_docs=2).load()

  # Format
  formatted_search_docs = "\n\n---\n\n".join(
    [
      f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}">\n{doc.page_content}\n</Document>'
      for doc in search_docs
    ]
  )

  return {"context": [formatted_search_docs]}


def generate_answer(state):
  """ Node to answer a question """

  # Get state
  context = state["context"]
  question = state["question"]

  # Template
  answer_template = """Answer the question {question} using this context: {context}"""
  answer_instructions = answer_template.format(question=question,
                                               context=context)

  # Answer
  answer = llm.invoke([SystemMessage(content=answer_instructions)] + [HumanMessage(content=f"Answer the question.")])

  # Append it to state
  return {"answer": answer}


builder = StateGraph(State)

# Initialize each node with node_secret
builder.add_node("search_web", search_web)
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("generate_answer", generate_answer)

# Flow
builder.add_edge(START, "search_wikipedia")
builder.add_edge(START, "search_web")
builder.add_edge("search_wikipedia", "generate_answer")
builder.add_edge("search_web", "generate_answer")
builder.add_edge("generate_answer", END)
graph = builder.compile()

print(graph.get_graph(xray=1).draw_mermaid())
graph.get_graph().print_ascii()


def main():
  result = graph.invoke({"question": "How were Nvidia's Q2 2024 earnings"})
  print(result["answer"].content)

if __name__ == "__main__":
  main()
