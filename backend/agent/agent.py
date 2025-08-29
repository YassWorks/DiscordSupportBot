from langchain_cerebras import ChatCerebras
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
import aiosqlite


LAST_N_TURNS = 10


class State(TypedDict):
    """Common state structure for all agents."""

    messages: Annotated[list[BaseMessage], add_messages]


def create_agent(
    model_name: str,
    api_key: str,
    tools: list,
    system_prompt: str,
    temperature: float = 0,
) -> CompiledStateGraph:
    """Create a base agent with common configuration and error handling.

    Args:
        model_name: The name of the model to use
        api_key: The API key for the model
        tools: List of tools to be used by the agent
        system_prompt: System prompt for the agent
        temperature: Temperature for the model

    Returns:
        Compiled state graph agent
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
        context = build_llm_context(state["messages"])
        return {"messages": [llm_chain.invoke({"messages": context})]}

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

    db_path = Path(__file__).resolve().parents[1] / "database"
    db_file = db_path / "memory.sqlite"

    conn = aiosqlite.connect(db_file.as_posix(), check_same_thread=False)
    mem = AsyncSqliteSaver(conn)

    compiled_graph = graph.compile(checkpointer=mem)

    return compiled_graph


def build_llm_context(messages: list[BaseMessage]):
    """
    Build the context for the LLM by including all messages after the last human message.
    And cleaning off anything before it.
    """
    new_context = []
    last_human_idx = len(messages) - 1

    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], HumanMessage):
            last_human_idx = i
            break

    new_context.extend(clean_context_window(messages[:last_human_idx]))
    new_context.extend(messages[last_human_idx:])

    return new_context


def clean_context_window(messages: list[BaseMessage]):
    """
    Clean the context window by keeping only the last N turns.
    And truncating the tools arguments for brevity.
    """
    new_context = []
    turn_count = 0

    for message in reversed(messages):

        if isinstance(message, HumanMessage):
            new_context.append(message)
            turn_count += 1
            if turn_count > LAST_N_TURNS:
                break

        elif isinstance(message, AIMessage):
            # strip all the tool_call related content for token efficiency
            if (
                hasattr(message, "content")
                and flatten_content(message.content).strip() != ""
            ):
                new_context.append(
                    AIMessage(
                        content=message.content,
                    )
                )

    new_context.reverse()
    return new_context


def flatten_content(content: list[str | dict]) -> str:
    """
    Flatten the content by joining strings or formatting dictionaries.
    """
    try:
        if isinstance(content, list):
            if isinstance(content[0], dict):
                content = "\n".join(
                    [f"{k}: {v}" for item in content for k, v in item.items()]
                )
            if isinstance(content[0], str):
                content = "\n".join(content)
        return content
    except Exception:
        return str(content)
