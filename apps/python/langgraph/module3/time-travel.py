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
from typing import Annotated
from operator import add
from langgraph.checkpoint.memory import MemorySaver

initialize_environment()

# llm = ChatOpenAI(model="gpt-4o")
llm = ChatOllama(model="llama3.1")  # or llama2, codellama, etc.
tools = [add, multiply, divide]

llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Node
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine the control flow
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

print(graph.get_graph().draw_mermaid())
graph.get_graph().print_ascii()

# Input
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}

# Thread
thread = {"configurable": {"thread_id": "1"}}

# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

def main():
  print("module 3")
  s = graph.get_state(thread)
  print(s)
  all_states = [s for s in graph.get_state_history(thread)]

  print(len(all_states))

if __name__ == "__main__":
  main()
