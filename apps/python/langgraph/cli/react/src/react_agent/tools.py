"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""
import uuid
from typing import Any, Callable, List, Optional, cast, Annotated

from langchain_tavily import TavilySearch  # type: ignore[import-not-found]

from .configuration import Configuration

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from langgraph.store.base import BaseStore

async def search(query: str) -> Optional[dict[str, Any]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    configuration = Configuration.from_context()
    wrapped = TavilySearch(max_results=configuration.max_search_results)
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))


async def upsert_memory(
  content: str,
  context: str,
  *,
  memory_id: Optional[uuid.UUID] = None,
  # Hide these arguments from the model.
  config: Annotated[RunnableConfig, InjectedToolArg],
  store: Annotated[BaseStore, InjectedToolArg],
):
  """Upsert a memory in the database.

  If a memory conflicts with an existing one, then just UPDATE the
  existing one by passing in memory_id - don't create two memories
  that are the same. If the user corrects a memory, UPDATE it.

  Args:
      content: The main content of the memory. For example:
          "User expressed interest in learning about French."
      context: Additional context for the memory. For example:
          "This was mentioned while discussing career options in Europe."
      memory_id: ONLY PROVIDE IF UPDATING AN EXISTING MEMORY.
      The memory to overwrite.
  """
  mem_id = memory_id or uuid.uuid4()
  user_id = Configuration.from_runnable_config(config).user_id
  await store.aput(
    ("memories", user_id),
    key=str(mem_id),
    value={"content": content, "context": context},
  )
  return f"Stored memory {mem_id}"


TOOLS: List[Callable[..., Any]] = [search]
