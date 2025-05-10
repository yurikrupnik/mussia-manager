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


class InputState(TypedDict):
  question: str


class OutputState(TypedDict):
  answer: str


class OverallState(TypedDict):
  question: str
  answer: str
  notes: str


def thinking_node(state: InputState):
  return {"answer": "bye", "notes": "... his is name is Lance"}


def answer_node(state: OverallState) -> OutputState:
  return {"answer": "bye Yuri"}


builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("answer_node", answer_node)
builder.add_node("thinking_node", thinking_node)
builder.add_edge(START, "thinking_node")
builder.add_edge("thinking_node", "answer_node")
builder.add_edge("answer_node", END)

# Add
graph = builder.compile()

print(graph.get_graph().draw_mermaid())
graph.get_graph().print_ascii()

def main():
  sd = graph.invoke({"questions": "hi"})
  print(sd)


if __name__ == "__main__":
  main()
