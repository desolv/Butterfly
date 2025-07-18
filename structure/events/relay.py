from discord.ext import commands

from structure.providers.helper import load_json_data
from structure.repo.services.relay_service import create_relay, delete_relay


class RelayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        environment = load_json_data(f"environment")
        self.enabled = environment["relay"]["enabled"]
        self.ignored_persona_id = environment["relay"]["ignored_persona_id"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.enabled or message.author.bot:
            return

        if message.author.id in self.ignored_persona_id:
            return

        try:
            names = [a.filename for a in message.attachments] if message.attachments else []
            has_files = bool(names)
            name_string = ",".join(names) if has_files else ""

            create_relay(
                user_id=message.author.id,
                message=f"{message.content[:1000]} {name_string}",
                message_id=message.id,
                channel_id=message.channel.id,
            )
        except Exception as e:
            print(f"Failed to log message → {e}")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        try:
            delete_relay(payload.message_id)
        except Exception as e:
            print(f"Failed to mark deleted → {e}")

async def setup(bot):
    await bot.add_cog(RelayCog(bot))
