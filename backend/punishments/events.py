import asyncio

import discord
from discord.ext import commands, tasks

from backend.punishments.director import get_global_active_expiring_punishments_within, get_user_active_punishment, \
    process_punishment_removal, create_or_update_punishment_config
from backend.punishments.models.punishment import PunishmentType


class PunishmentEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_expiring_punishments.start()

    def cog_unload(self):
        self.check_expiring_punishments.cancel()

    @tasks.loop(seconds=30)
    async def check_expiring_punishments(self):
        for punishment in get_global_active_expiring_punishments_within():
            if not punishment.has_expired:
                continue

            guild = self.bot.get_guild(punishment.guild_id)

            await process_punishment_removal(
                self.bot,
                guild,
                punishment,
                self.bot.user,
                "Automatic"
            )

    @check_expiring_punishments.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        muted_role_id = create_or_update_punishment_config(after.guild.id).muted_role_id
        muted_role = after.guild.get_role(muted_role_id)

        if not muted_role:
            return

        if muted_role in before.roles and muted_role not in after.roles:
            await asyncio.sleep(1)

            async for entry in after.guild.audit_logs(
                    limit=5,
                    action=discord.AuditLogAction.member_role_update
            ):
                if entry.target.id == after.id and muted_role in entry.changes.before.roles:
                    actioner = entry.user
                    reason = entry.reason
                    break
            else:
                actioner = None
                reason = None

            punishment = get_user_active_punishment(after.guild.id, after.id, PunishmentType.MUTE)
            guild = self.bot.get_guild(punishment.guild_id)
            reason = reason if reason else "No reason"

            await process_punishment_removal(
                self.bot,
                guild,
                punishment,
                actioner,
                reason
            )


async def setup(bot):
    await bot.add_cog(PunishmentEvents(bot))
