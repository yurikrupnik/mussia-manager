from mylibrary import initialize_environment
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage

initialize_environment()

# llm = ChatOpenAI(model="gpt-4o")
llm = ChatOllama(model="llama3.1")  # or llama2, codellama, etc.

# Node
def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"][-1:])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()


def main():
  # Message list with a preamble
  messages = [AIMessage("Hi.", name="Bot", id="1")]
  messages.append(HumanMessage("Hi.", name="Lance", id="2"))
  messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
  messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Lance", id="4"))
  # Invoke
  output = graph.invoke({'messages': messages})
  print(output['messages'])
  for m in output['messages']:
    m.pretty_print()
  messages.append(output['messages'][-1])
  messages.append(HumanMessage(f"Tell me more about Narwhals!", name="Lance"))


if __name__ == "__main__":
  main()
