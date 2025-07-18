import discord
from discord.ext import commands, tasks

from structure.providers.helper import load_json_data
from structure.repo.services.punishment_service import get_active_punishments, deactivate_punishment
from structure.repo.models.punishment_model import PunishmentType


class Punishment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        environment = load_json_data(f"environment")
        self.guild_id = environment["guild_id"]
        self.muted_role = environment["punishments"]["muted_role"]
        self.check_punishments.start()

    def cog_unload(self):
        self.check_punishments.cancel()

    @tasks.loop(minutes=30)
    async def check_punishments(self):
        expired = get_active_punishments()

        for punishment in expired:
            guild = self.bot.get_guild(self.guild_id)
            member = guild.get_member(punishment.user_id)
            try:
                if punishment.type == PunishmentType.MUTE and member:
                    role = guild.get_role(self.muted_role)
                    if role and role in member.roles:
                        await member.remove_roles(role, reason="Mute expired")

                elif punishment.type == PunishmentType.BAN:
                        bans = await guild.bans()
                        if any(ban_entry.user.id == punishment.user_id for ban_entry in bans):
                            await guild.unban(discord.Object(id=punishment.user_id), reason="Tempban expired")

                deactivate_punishment(punishment.id)
            except Exception as e:
                print(f"Failed to remove punishment #{punishment.id} → {e}")

    @check_punishments.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Punishment(bot))
