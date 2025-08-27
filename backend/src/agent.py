from langchain_cerebras import ChatCerebras
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
import sqlite3


class State(TypedDict):
    """Common state structure for all agents."""
    messages: Annotated[list[BaseMessage], add_messages]


def create_base_agent(
    model_name: str,
    api_key: str,
    tools: list,
    system_prompt: str,
    temperature: float = 0,
    include_graph: bool = False,
) -> CompiledStateGraph | tuple[StateGraph, CompiledStateGraph]:
    """Create a base agent with common configuration and error handling.

    Args:
        model_name: The name of the model to use
        api_key: The API key for the model
        tools: List of tools to be used by the agent
        system_prompt: System prompt for the agent
        temperature: Temperature for the model
        include_graph: Whether to include the graph in the response

    Returns:
        Compiled state graph agent or tuple of (graph, compiled_graph)
    """

    llm = ChatCerebras(
        model=model_name,
        temperature=temperature,
        timeout=None,
        max_retries=5,
        api_key=api_key,
    )

    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ]
    )

    if tools:
        llm_with_tools = llm.bind_tools(tools)
    else:
        llm_with_tools = llm
    llm_chain = template | llm_with_tools
    graph = StateGraph(State)

    def llm_node(state: State):
        return {"messages": [llm_chain.invoke({"messages": state["messages"]})]}

    tool_node = ToolNode(tools=tools, handle_tool_errors=False)

    graph.add_node("llm", llm_node)

    if tools:
        graph.add_node("tools", tool_node)
        graph.add_edge(START, "llm")
        graph.add_conditional_edges("llm", tools_condition)
        graph.add_edge("tools", "llm")
    else:
        graph.add_edge(START, "llm")
        graph.add_edge("llm", END)

    db_path = (Path(__file__).resolve().parents[1] / "database")
    db_file = db_path / "memory.sqlite"
    conn = sqlite3.connect(db_file.as_posix(), check_same_thread=False)

    mem = SqliteSaver(conn)
    built_graph = graph.compile(checkpointer=mem)

    if include_graph:
        return graph, built_graph
    else:
        return built_graph
