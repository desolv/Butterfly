# -*- coding: utf-8 -*-
import asyncio
import os

import nest_asyncio
from dotenv import load_dotenv

from backend.core.database import Engine, init_tables

nest_asyncio.apply()

import platform
import sys
from datetime import datetime

import discord
from discord.ext import commands
from pathlib import Path

from openai import OpenAI
from backend.core.helper import format_time_in_zone

load_dotenv(f"io/.env")

bot = commands.Bot(command_prefix="?", help_command=None, intents=discord.Intents.all())
bot.client = OpenAI(api_key=os.getenv("OPENAI"))

print(f"Butterfly Robot")
print(f"Running at Python {platform.python_version()}v, "
      f"Discord.py {discord.__version__}v - {platform.system()} {platform.release()} ({os.name})")

try:
    postgre_uptime = datetime.now()
    with Engine.connect() as connection:
        print(f"Running PostgreSQL with SQLAlchemy at {str(format_time_in_zone(postgre_uptime, format="%S"))}ms")
    init_tables()
except Exception as e:
    print(f"Failed to connect to PostgreSQL -> {e}")
    sys.exit(0)

try:
    test_response = bot.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Ping"}]
    )
    print("Connected to OpenAI")
except Exception as e:
    print(f"Failed to connect to OpenAI -> {e}")
    sys.exit(0)


async def load():
    skip_folders = {".venv", "io"}
    skip_file_names = {"database.py", "models.py", "butterfly.py"}

    for extension in Path("backend").rglob("*.py"):
        if (
                extension.stem.startswith("__")
                or "models" in extension.parts
                or any(folder in extension.parts for folder in skip_folders)
                or extension.name in skip_file_names
        ):
            continue

        ext_path = ".".join(extension.with_suffix("").parts)
        try:
            await bot.load_extension(ext_path)
        except commands.NoEntryPointError:
            continue


async def main():
    await load()
    await bot.start(os.getenv("TOKEN"))


asyncio.run(main())
