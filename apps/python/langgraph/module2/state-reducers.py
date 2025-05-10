from mylibrary import initialize_environment
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from typing_extensions import TypedDict
from typing import Literal, Any, Self
import random
from dataclasses import dataclass
from pydantic import BaseModel, field_validator, ValidationError
from typing import Annotated
from operator import add

initialize_environment()

# llm = ChatOpenAI(model="gpt-4o")
llm = ChatOllama(model="llama3.1")  # or llama2, codellama, etc.


def reduce_list(left: list | None, right: list | None) -> list:
  """Safely combine two lists, handling cases where either or both inputs might be None.

  Args:
      left (list | None): The first list to combine, or None.
      right (list | None): The second list to combine, or None.

  Returns:
      list: A new list containing all elements from both input lists.
             If an input is None, it's treated as an empty list.
  """
  if not left:
    left = []
  if not right:
    right = []
  return left + right

def node_1(state):
    print("---Node 1---")
    return {"foo": [2]}

class DefaultState(TypedDict):
  foo: Annotated[list[int], add]


class CustomReducerState(TypedDict):
  foo: Annotated[list[int], reduce_list]

# Build graph
builder = StateGraph(CustomReducerState)
builder.add_node("node_1", node_1)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

# Add
graph = builder.compile()

print(graph.get_graph().draw_mermaid())
graph.get_graph().print_ascii()

def main():
  messages = [AIMessage("Hi.", name="Bot", id="1")]
  messages.append(HumanMessage("Hi.", name="Lance", id="2"))
  messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
  messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Lance", id="4"))

  # Isolate messages to delete
  delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
  add_messages(messages , delete_messages)
  print(messages)


if __name__ == "__main__":
  main()
