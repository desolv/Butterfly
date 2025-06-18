import asyncio
import nest_asyncio
nest_asyncio.apply()

import os
import platform
import sys
from datetime import datetime

import discord
from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path

from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from structure.helper import get_formatted_time, load_json_data

STATE = "development"

load_dotenv(f"schema/.env.{STATE}")

TOKEN = os.getenv("TOKEN")
MYSQL = os.getenv("MYSQL")
DEBUG = os.getenv("DEBUG")
OPENAI = os.getenv("OPENAI")

design_schema = load_json_data(f"design.{STATE}")
bot = commands.Bot(command_prefix=design_schema["command_prefix"], intents=discord.Intents.all())
bot.engine = create_engine(MYSQL, echo=(True if DEBUG == "True" else False))
bot.base = declarative_base()
bot.client = OpenAI(api_key=OPENAI)

print(f"Snowy {STATE} Robot")
print(f"Running at Python {platform.python_version()}v, "
      f"Discord.py {discord.__version__}v - {platform.system()} {platform.release()} ({os.name})")

try:
    mysql_uptime = datetime.now()
    with bot.engine.connect() as connection:
        print(f"Running MySQL with SQLAlchemy at {str(get_formatted_time(mysql_uptime, format="%S"))}ms")
except Exception as e:
    print(f"Failed to connect to MySQL -> {e}")
    sys.exit(0)

try:
    test_response = bot.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Ping"}]
    )
    print("Connected to OpenAI\n")
except Exception as e:
    print(f"Failed to connect to OpenAI -> {e}")
    sys.exit(0)


async def load():
    for extension in Path("structure").rglob("*.py"):
        if extension.stem.startswith("__") or "tables" in extension.parts:
            continue

        if extension.stem != "__init__":
            ext_path = ".".join(extension.parts).replace(".py", "")
            try:
                await bot.load_extension(ext_path)
            except commands.NoEntryPointError:
                print(f"Skipped loading extension '{extension.stem}' as it does not have a 'setup' function")


async def main():
    await load()
    await bot.start(TOKEN)


asyncio.run(main())
