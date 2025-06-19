from discord.ext import commands
from structure.repo.services.logbook_service import create_logbook, delete_logbook

class TrackerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            names = [a.filename for a in message.attachments] if message.attachments else []
            has_files = bool(names)
            name_string = ",".join(names) if has_files else ""

            create_logbook(
                discord_id=message.author.id,
                message=f"{message.content[:1000]} {name_string}",
                message_id=message.id,
                channel_id=message.channel.id,
            )
        except Exception as e:
            print(f"Failed to log message → {e}")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        try:
            delete_logbook(payload.message_id)
        except Exception as e:
            print(f"Failed to mark deleted → {e}")

async def setup(bot):
    await bot.add_cog(TrackerCog(bot))
