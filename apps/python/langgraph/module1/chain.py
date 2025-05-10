from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langchain_ollama import ChatOllama
from typing_extensions import TypedDict
# from langchain_core.messages import AnyMessage
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    pass

# messages = [AIMessage(content=f"So you said you were researching ocean mammals?", name="Model")]
# messages.append(HumanMessage(content=f"Yes, that's right.",name="Lance"))
# messages.append(AIMessage(content=f"Great, what would you like to learn about.", name="Model"))
# messages.append(HumanMessage(content=f"I want to learn about the best place to see Orcas in the US.", name="Lance"))
#
# for m in messages:
#     m.pretty_print()

llm = ChatOllama(model="llama3.1")  # or llama2, codellama, etc.
# result = llm.invoke(messages)

def multiply(a: int, b: int) -> int:
  """Multiply a and b.

  Args:
      a: first int
      b: second int
  """
  return a * b

llm_with_tools = llm.bind_tools([multiply])

# initial_messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
#                     HumanMessage(content="I'm looking for information on marine biology.", name="Yuri")
#                    ]

# New message to add
# new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")

# Test
# add_messages(initial_messages , new_message)


# Node
def tool_calling_llm(state: MessagesState):
  return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply]))
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", END)
graph = builder.compile()

def main():
  messages = graph.invoke({"messages": HumanMessage(content="Hello!")})
  for m in messages['messages']:
    m.pretty_print()
  messages = graph.invoke({"messages": HumanMessage(content="Multiply 2 and 3")})
  for m in messages['messages']:
    m.pretty_print()
  # print(result)
  # print(result.response_metadata)
  # tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 5 multiplied by 3", name="Lance")])
  # print(tool_call.tool_calls)


if __name__ == "__main__":
  main()
