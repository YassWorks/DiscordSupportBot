def strip_thinking_block(raw_response: str) -> str:
    return raw_response[raw_response.find("</think>") + len("</think>") :].strip()
