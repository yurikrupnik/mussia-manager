from mylibrary import initialize_environment, add, multiply, divide
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

initialize_environment()

tools = [add, multiply, divide]
llm = ChatOllama(model="llama3.1")

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

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")
react_graph = builder.compile()

memory = MemorySaver()
react_graph_memory = builder.compile(checkpointer=memory)

# Specify a thread
config = {"configurable": {"thread_id": "1"}}

# Step 1: First interaction
messages = [HumanMessage(content="Add 3 and 4.")]
response = react_graph_memory.invoke({"messages": messages}, config)

# Store full conversation so far
messages = response["messages"]

# Step 2: Add next message in the same conversation context
messages.append(HumanMessage(content="Multiply that by 2."))
response = react_graph_memory.invoke({"messages": messages}, config)

# Print final result
for m in response["messages"]:
    m.pretty_print()

