def strip_thinking_block(raw_response: str) -> str:
    return (
        raw_response[raw_response.find("</think>") + len("</think>") :].strip()
        if "</think>" in raw_response
        else raw_response.strip()
    )
