from fastapi import FastAPI
from backend import SupportAgent
from dotenv import load_dotenv
import os


load_dotenv()


API_KEY = os.getenv("CEREBRAS_API_KEY")
MODEL_NAME = "qwen-3-32b"
TEMPERATURE = 0


agent = SupportAgent(
    api_key=API_KEY,
    model_name=MODEL_NAME,
    temperature=TEMPERATURE,
)


app = FastAPI(description="Member Discord Support Agent API",)


@app.get("/prompt/{prompt}")
async def get_prompt_response(prompt: str):
    response = await agent.get_response(prompt)
    return response
