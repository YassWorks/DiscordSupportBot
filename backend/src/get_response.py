from backend.agent.agent import create_agent
from langchain_core.messages import AIMessage
from backend.helpers.strip_thinking import strip_thinking_block
from backend.agent.tools import TOOLS
from pathlib import Path
import openai


PROMPTS_PATH = Path(__file__).resolve().parents[1] / "prompts"
RECURSION_LIMIT = 100


class SupportAgent:

    def __init__(
        self,
        api_key: str,
        model_names: str | list[str],
        temperature: float = 0,
    ):
        self.api_key = api_key
        self.model_names = (
            [model_names] if isinstance(model_names, str) else model_names
        )
        self.current_model_index = 0
        self.temperature = temperature

        system_prompt_path = PROMPTS_PATH / "system_prompt.txt"
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        self.system_prompt = system_prompt.strip() or "You are a helpful assistant."

        self.agent = create_agent(
            model_name=self.model_names[0],
            api_key=api_key,
            tools=TOOLS,
            system_prompt=self.system_prompt,
            temperature=temperature,
        )

    async def get_response(self, prompt: str, member_username: str) -> str:

        configuration = {
            "configurable": {"thread_id": f"{member_username or 'default_user'}"},
            "recursion_limit": RECURSION_LIMIT,
        }
        
        error_msg = "Sorry mate, the service is currently experiencing high demand. Please try again later."
        response = {}

        while self.current_model_index < len(self.model_names):
            try:
                response = await self.agent.ainvoke(
                    {"messages": [("human", prompt)]}, config=configuration
                )
                break

            except openai.RateLimitError:

                self.current_model_index += 1
                if self.current_model_index >= len(self.model_names):
                    return error_msg

                # switch to next model
                self.agent = create_agent(
                    model_name=self.model_names[self.current_model_index],
                    api_key=self.api_key,
                    tools=TOOLS,
                    system_prompt=self.system_prompt,
                    temperature=self.temperature,
                )

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
