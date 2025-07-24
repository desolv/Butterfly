import re
from datetime import datetime

import discord
from discord.ext import commands, tasks

from structure.providers.helper import load_json_data


def should_modify_message(content: str) -> tuple[str, bool]:
    message = content.strip()
    message = message[:300] if len(message) > 300 else message

    if not message or len(message) < 2 or all(char in "!?@#/><&^%$£!. " for char in message):
        return message, False

    if re.search(r"(.)\1{4,}", message):
        return message, False

    return message, True


def parse_gpt_verdicts(raw: str) -> dict[int, str]:
    results = {}
    for line in raw.splitlines():
        match = re.match(r"\[(\d+)]\s+Verdict:\s+(.*)", line)
        if match:
            idx = int(match.group(1))
            verdict = match.group(2).strip()
            results[idx] = verdict
    return results


async def is_inappropriate_batch(client, gpt_prompt, messages: list[str]) -> str:
    prompt = gpt_prompt + "\n".join(f"[{i + 1}] {msg}" for i, msg in enumerate(messages))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI failed → {e}")
        return ""


class WatcherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        environment = load_json_data(f"environment")
        self.guild_id = environment["guild_id"]
        self.enabled = environment["watcher"]["enabled"]
        self.monitor_channel = environment["watcher"]["moderation_channel"]
        self.watching_channels = environment["watcher"]["watching_channels"]
        self.watching_categories = environment["watcher"]["watching_categories"]
        self.batch_loop_seconds = environment["watcher"]["batch"]["batch_loop_seconds"]
        self.batch_loop_messages = environment["watcher"]["batch"]["batch_loop_messages"]
        self.prompt = environment["watcher"]["prompt"]
        self.client = bot.client
        self.batch_queue = []
        self.batch_loop.start()

    def cog_unload(self):
        self.batch_loop.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.enabled or (self.guild_id != message.guild.id):
            return

        channel_ok = message.channel.id in self.watching_channels
        category_ok = (
                message.channel.category and
                message.channel.category.id in self.watching_categories
        )

        if message.author.bot or not (channel_ok or category_ok):
            return

        cleaned_message, should_check = should_modify_message(message.content)

        if not should_check:
            return

        self.batch_queue.append((message, cleaned_message))

        if 0 < self.batch_loop_messages <= len(self.batch_queue):
            await self.process_batch()

    @tasks.loop(seconds=1)
    async def batch_loop(self):
        await self.process_batch()

    @batch_loop.before_loop
    async def before_batch_loop(self):
        await self.bot.wait_until_ready()

        if self.batch_loop_seconds <= 0:
            self.batch_loop.cancel()
            return

        self.batch_loop.change_interval(seconds=self.batch_loop_seconds)

    async def process_batch(self):
        if not self.batch_queue:
            return

        batch = self.batch_queue
        self.batch_queue = []
        cleaned_messages = [cleaned for _, cleaned in batch]

        raw_verdicts = await is_inappropriate_batch(self.client, self.prompt, cleaned_messages)
        verdicts = parse_gpt_verdicts(raw_verdicts)

        mod_channel = self.bot.get_channel(self.monitor_channel)
        if not mod_channel:
            return

        embed = discord.Embed(
            title=f"ʙᴀᴛᴄʜ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ʀᴇѕᴜʟᴛѕ",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (msg, cleaned) in enumerate(batch):
            verdict_text = verdicts.get(i + 1, "No result provided")

            embed.add_field(
                name=" ",
                value=f"""
                **ᴘᴇʀѕᴏɴᴀ**: {msg.author.mention}
                **ᴄʜᴀɴɴᴇʟ**: {msg.channel.mention}
                **ᴠᴇʀᴅɪᴄᴛ**: {verdict_text}
                **ᴍᴇѕѕᴀɢᴇ**: {cleaned}
                **ᴛɪᴍᴇ**: {msg.added_at.strftime('%H:%M:%S')}""",
                inline=False
            )

        embed.add_field(name=" ", value=f"**ʙᴀᴛᴄʜ ᴛɪᴍᴇ**: {datetime.utcnow().strftime('%d %B %Y %H:%M GMT')}")

        await mod_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WatcherCog(bot))
