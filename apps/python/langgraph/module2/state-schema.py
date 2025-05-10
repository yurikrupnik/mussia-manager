from mylibrary import initialize_environment
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from typing import Literal
import random
from pydantic import BaseModel, field_validator

initialize_environment()

class PydanticState(BaseModel):
    name: str
    mood: str

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, value):
      if value not in ["happy", "sad"]:
        raise ValueError("Invalid mood")
      return value

# llm = ChatOpenAI(model="gpt-4o")
llm = ChatOllama(model="llama3.1")  # or llama2, codellama, etc.


def node_1(state):
  print("---Node 1---")
  return {"name": state.name + " is ... "}


def node_2(state):
  print("---Node 2---")
  return {"mood": "happy"}


def node_3(state):
  print("---Node 3---")
  return {"mood": "sad"}


def decide_mood(state) -> Literal["node_2", "node_3"]:
  # Here, let's just do a 50 / 50 split between nodes 2, 3
  if random.random() < 0.5:
    # 50% of the time, we return Node 2
    return "node_2"

  # 50% of the time, we return Node 3
  return "node_3"


# Build graph
builder = StateGraph(PydanticState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)


# Add
graph = builder.compile()

print(graph.get_graph().draw_mermaid())
graph.get_graph().print_ascii()

def main():
  # Message list with a preamble
  print("aris")
  te = graph.invoke(PydanticState(name="yuri", mood="sad"))
  print(te)

if __name__ == "__main__":
  main()
