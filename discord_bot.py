from backend import SupportAgent
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
from datetime import datetime


handler = logging.FileHandler(filename=f"logs/{datetime.now().strftime('%Y-%m-%d')}.log", encoding='utf-8', mode='w')
load_dotenv()


TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("CEREBRAS_API_KEY")
MODEL_NAME = "qwen-3-32b"
TEMPERATURE = 0


intents = discord.Intents.default()
intents.message_content = True
intents.presences = True


bot = commands.Bot(command_prefix="/", intents=intents)
agent = None


@bot.event
async def on_ready():
    global agent
    agent = SupportAgent(
        api_key=API_KEY,
        model_name=MODEL_NAME,
        temperature=TEMPERATURE,
    )


@bot.command(name="ask")
async def ask(ctx):
    response = await agent.get_response(ctx.message.content, ctx.author.name)
    await ctx.send(f"**{ctx.author.mention}**: {response}")


bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
