from discord.ext import commands

from structure.providers.helper import load_json_data
from structure.repo.services.tracking_service import create_track, remove_user_track


class TrackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        environment = load_json_data(f"environment")
        self.guild_id = environment["guild_id"]
        self.enabled = environment["relay"]["enabled"]
        self.exempt_users = environment["relay"]["exempt_users"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.enabled or message.author.bot or (self.guild_id != message.guild.id):
            return

        if message.author.id in self.exempt_users:
            return

        try:
            names = [a.filename for a in message.attachments] if message.attachments else []
            has_files = bool(names)
            name_string = ",".join(names) if has_files else ""

            create_track(
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
            remove_user_track(payload.message_id)
        except Exception as e:
            print(f"Failed to mark deleted → {e}")


async def setup(bot):
    await bot.add_cog(TrackCog(bot))
