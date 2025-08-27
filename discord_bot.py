from backend import SupportAgent
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


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
    print(f"Logged in as {bot.user.name}")
    

@bot.command(name="ask")
async def ask(ctx):
    response = await agent.get_response(ctx.message.content)
    await ctx.send(f"**{ctx.author.mention}**: {response}")


bot.run(TOKEN)