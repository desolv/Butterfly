import re
from datetime import datetime

from discord.ext import commands, tasks

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


async def is_inappropriate_batch(client, messages: list[str]) -> str:
    prompt = (
            "You are a Discord moderation assistant."
            "Judge the following messages and respond in this exact format: "
            "[1] Verdict: Safe/Flagged/Unsure - [short reason] "
            "`Safe` - if the message is harmless. "
            "`Flagged` - if it's extremely toxic, threatening, NSFW, slur-filled or a serious rule violation."
            "`Unsure` - if the message lacks context or is unclear. "
            "Ignore emojis, memes, links, and jokes unless clearly harmful. "
            "Messages: " +
            "\n".join(f"[{i + 1}] {msg}" for i, msg in enumerate(messages))
    )

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
        self.monitor_channel_id = bot.schema["watcher"]["moderation_channel_id"]
        self.watching_channel_id = bot.schema["watcher"]["watching_channel_id"]
        self.watching_category_id = bot.schema["watcher"]["watching_category_id"]
        self.client = bot.client
        self.batch_queue = []
        self.batch_loop.start()

    def cog_unload(self):
        self.batch_loop.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        channel_ok = message.channel.id in self.watching_channel_id
        category_ok = message.channel.category.id in self.watching_category_id

        if message.author.bot or not (channel_ok or category_ok):
            return

        cleaned_message, should_check = should_modify_message(message.content)

        if not should_check:
            return

        self.batch_queue.append((message, cleaned_message))

        if len(self.batch_queue) >= 5:
            await self.process_batch()

    @tasks.loop(seconds=30)
    async def batch_loop(self):
        await self.process_batch()

    async def process_batch(self):
        if not self.batch_queue:
            return

        batch = self.batch_queue
        self.batch_queue = []
        cleaned_messages = [cleaned for _, cleaned in batch]

        raw_verdicts = await is_inappropriate_batch(self.client, cleaned_messages)
        verdicts = parse_gpt_verdicts(raw_verdicts)

        mod_channel = self.bot.get_channel(self.monitor_channel_id)
        if not mod_channel:
            return

        lines = ["```ansi", "\u001b[1;37mBatch Moderation Results:\u001b[0m"]

        for i, (msg, cleaned) in enumerate(batch):
            verdict_text = verdicts.get(i + 1, "Unknown")
            verdict_lower = verdict_text.lower()
            verdict_color = "\u001b[1;32m"

            if verdict_lower.startswith("flagged"):
                verdict_color = "\u001b[1;31m"
            elif verdict_lower.startswith("unsure"):
                verdict_color = "\u001b[1;33m"

            lines.append(f"\n\u001b[1;37mUser:\u001b[0m {msg.author}")
            lines.append(f"\u001b[1;37mChannel:\u001b[0m #{msg.channel.name}")
            lines.append(f"\u001b[1;37mVerdict:\u001b[0m {verdict_color}{verdict_text}\u001b[0m")
            lines.append(f"\u001b[1;37mMessage:\u001b[0m {cleaned}")
            lines.append(f"\u001b[1;37mTime:\u001b[0m {msg.created_at.strftime('%H:%M:%S')}")

        lines.append("\n\u001b[1;37mBatch Time:\u001b[0m " + datetime.utcnow().strftime('%d %B %Y %H:%M GMT'))
        lines.append("```")
        await mod_channel.send("\n".join(lines))


async def setup(bot):
    await bot.add_cog(WatcherCog(bot))
