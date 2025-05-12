from mylibrary import initialize_environment
import pathlib
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph
from src.chains import generation_chain, reflection_chain
from typing import List, Sequence

REFLECT = "reflect"
GENERATE = "generate"


def generation_node(state: Sequence[BaseMessage]):
    return generation_chain.invoke({"messages": state})


def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    res = reflection_chain.invoke({"messages": messages})
    return [HumanMessage(content=res.content)]


def should_continue(state: List[BaseMessage]):
    if len(state) > 3:
        return END
    return REFLECT


builder = MessageGraph()
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.set_entry_point(GENERATE)
builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)

graph = builder.compile()
print(graph.get_graph().draw_mermaid())
graph.get_graph().print_ascii()


def main():
    # Get the current file's directory and find the .env file
    current_dir = pathlib.Path(__file__).parent
    dotenv_path = current_dir / ".env"
    initialize_environment(str(dotenv_path))
    inputs = HumanMessage(
        content="""
        Make this tweet better:
        @LangChainAI
        - newly Tool Calling feature is a seriously underrated.
        After a long wait, it's here - making the implementation of agents across different models with function calling - supper easy.
        Made a video covering their newest blog post
      """,
    )
    response = graph.invoke(inputs)
    print(response)


if __name__ == "__main__":
    main()
