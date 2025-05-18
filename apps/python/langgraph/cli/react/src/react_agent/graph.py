"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""
import asyncio
from datetime import UTC, datetime
from typing import Dict, List, Literal, cast

from langchain.agents import Agent
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.store.base import BaseStore

from mylibrary import initialize_environment

from .configuration import Configuration
from .state import InputState, State
from .tools import TOOLS, upsert_memory
from .utils import load_chat_model
from .memory import checkpointer

# Define the function that calls the model
initialize_environment()

import os
print("The value is: " + os.environ.get("OPENAI_API_KEY", "") + " and it's important.")
print("Redis: " + os.environ.get("REDIS_URI_CUSTOM", "") + " and it's important.")


async def call_model2(state: State) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    configuration = Configuration.from_context()

    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(configuration.model).bind_tools(TOOLS)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = configuration.system_prompt.format(
        system_time=datetime.now(tz=UTC).isoformat()
    )

    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages]
        ),
    )

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response as a list to be added to existing messages
    return {"messages": [response]}


async def store_memory(state: State, config: RunnableConfig, *, store: BaseStore):
  # Extract tool calls from the last message
  tool_calls = state.messages[-1].tool_calls

  # Concurrently execute all upsert_memory calls
  saved_memories = await asyncio.gather(
    *(
      upsert_memory(**tc["args"], config=config, store=store)
      for tc in tool_calls
    )
  )

  # Format the results of memory storage operations
  # This provides confirmation to the model that the actions it took were completed
  results = [
    {
      "role": "tool",
      "content": mem,
      "tool_call_id": tc["id"],
    }
    for tc, mem in zip(tool_calls, saved_memories)
  ]
  return {"messages": results}


# Define a new graph

builder = StateGraph(State, input=InputState, config_schema=Configuration)

# Define the two nodes we will cycle between
builder.add_node(call_model2)
builder.add_node("tools", ToolNode(TOOLS))
# builder.add_node(store_memory)
# Set the entrypoint as `call_model2`
# This means that this node is the first one called
builder.add_edge("__start__", "call_model2")
# builder.add_edge("store_memory", "call_model2")

def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "__end__"
    # Otherwise we execute the requested actions
    return "tools"


def upsert_memory(key: str, value: str, config: RunnableConfig, store: BaseStore):
  store.set(...), store.get(...)  # depends on the implementation of your tools

# Add a conditional edge to determine the next step after `call_model2`
builder.add_conditional_edges(
    "call_model2",
    # After call_model2 finishes running, the next node(s) are scheduled
    # based on the output from route_model_output
    route_model_output,
# ["store_memory", END]
)

# Add a normal edge from `tools` to `call_model2`
# This creates a cycle: after using tools, we always return to the model
builder.add_edge("tools", "call_model2")

config = {
    "configurable": {
        "thread_id": "1"
    }
}

# Compile the builder into an executable graph
graph = builder.compile(name="ReAct Agent")
