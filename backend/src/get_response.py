from backend.agent.agent import create_agent
from langchain_core.messages import AIMessage
from backend.helpers.strip_thinking import strip_thinking_block
from backend.agent.tools import tools
from pathlib import Path
import openai


PROMPTS_PATH = Path(__file__).resolve().parents[1] / "prompts"
RECURSION_LIMIT = 100


class SupportAgent:

    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float = 0,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature

        system_prompt_path = PROMPTS_PATH / "system_prompt.txt"
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        self.agent = create_agent(
            model_name=model_name,
            api_key=api_key,
            tools=tools,
            system_prompt=system_prompt.strip() or "You are a helpful assistant.",
            temperature=temperature,
        )

    async def get_response(self, prompt: str) -> str:

        member_username = "user123"

        configuration = {
            "configurable": {"thread_id": f"{member_username}"},
            "recursion_limit": RECURSION_LIMIT,
        }
        error_msg = "Sorry mate, an error occurred. Please try again later."

        try:
            response = await self.agent.ainvoke(
                {"messages": [("human", prompt)]}, config=configuration
            )
            
        except openai.RateLimitError:
            return "Sorry mate, the service is currently experiencing high demand. Please try again later."
        
        except Exception:
            return error_msg

        messages = response.get("messages", [])
        if (
            messages
            and isinstance(messages[-1], AIMessage)
            and hasattr(messages[-1], "content")
        ):
            return strip_thinking_block(messages[-1].content)
        else:
            return error_msg