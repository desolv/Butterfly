import asyncio
import json
import os
import platform

import discord
from dotenv import load_dotenv
from discord.ext import commands

STATE = "development"

load_dotenv(f"schema/.env.{STATE}")

TOKEN = os.getenv("TOKEN")
MYSQL = os.getenv("MYSQL")

with open(f"schema/design.{STATE}.json", "r") as file:
    schema = json.load(file)

bot = commands.Bot(command_prefix=schema["command_prefix"], intents=discord.Intents.all())

print(f"Snowy {STATE} Robot Running")
print(f"Running at Python {platform.python_version()}v, "
      f"Discord.py {discord.__version__}v - {platform.system()} {platform.release()} ({os.name})\n")


async def main():
    await bot.start(TOKEN)

asyncio.run(main())
