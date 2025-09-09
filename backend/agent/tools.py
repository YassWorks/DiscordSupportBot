from langchain_core.tools import tool
from pathlib import Path


PROMPTS_DIR = Path(__file__).parents[1] / "prompts"


@tool
def get_ains_prompt() -> str:
    """Retrieves the AINS event info."""
    prompt_path = PROMPTS_DIR / "ains.txt"
    return prompt_path.read_text(encoding="utf-8")


@tool
def get_data_overflow_prompt() -> str:
    """Retrieves the Data Overflow event info."""
    prompt_path = PROMPTS_DIR / "data_overflow.txt"
    return prompt_path.read_text(encoding="utf-8")


@tool
def get_orbit_prompt() -> str:
    """Retrieves the Orbit event info."""
    prompt_path = PROMPTS_DIR / "orbit.txt"
    return prompt_path.read_text(encoding="utf-8")


@tool
def get_xtreme_prompt() -> str:
    """Retrieves the IEEEXtreme event info."""
    prompt_path = PROMPTS_DIR / "xtreme.txt"
    return prompt_path.read_text(encoding="utf-8")


TOOLS = [
    get_ains_prompt,
    get_data_overflow_prompt,
    get_orbit_prompt,
    get_xtreme_prompt,
]
