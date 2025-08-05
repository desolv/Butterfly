import asyncio

import discord
from discord.ext import commands, tasks

from backend.configs.manager import get_punishment_settings
from backend.core.helper import send_private_dm
from backend.punishments.manager import get_global_active_expiring_punishments_within, remove_user_active_punishment, \
    send_punishment_moderation_log, get_user_active_punishment
from backend.punishments.models import PunishmentType


class PunishmentEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_expiring_punishments.start()

    def cog_unload(self):
        self.check_expiring_punishments.cancel()

    @tasks.loop(seconds=30)
    async def check_expiring_punishments(self):
        for punishment in get_global_active_expiring_punishments_within():
            if not punishment.has_expired():
                continue

            muted_role, _, _, _, _ = get_punishment_settings(punishment.guild_id)

            guild = self.bot.get_guild_data(punishment.guild_id)

            match punishment.punishment_type:
                case PunishmentType.MUTE:
                    try:
                        member = guild.get_member(punishment.user_id)
                        muted_role = guild.get_role(muted_role)
                        await member.remove_roles(muted_role, reason="Automatic")
                    except Exception as e:
                        print(f"Wasn't able remove mute for {punishment.user_id}. Aborting! -> {e}")
                        continue

                    sent_dm = await send_private_dm(member,
                                                    f"Hey! **You're able to chat now!** Please refrain from breaking rules again.")
                case PunishmentType.BAN:
                    try:
                        await guild.unban(discord.Object(id=punishment.user_id), reason="Automatic")
                    except Exception as e:
                        print(f"Wasn't able remove ban for {punishment.user_id}. Aborting! -> {e}")
                        continue

                    try:
                        member = await self.bot.fetch_user(punishment.user_id)
                    except Exception:
                        member = None

                    sent_dm = False
                case _:
                    continue

            removed_punishment, success = remove_user_active_punishment(punishment.guild_id, punishment.punishment_id,
                                                                        reason="Automatic")

            await send_punishment_moderation_log(
                guild,
                member,
                self.bot.user,
                removed_punishment,
                sent_dm,
                removed=True
            )

    @check_expiring_punishments.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        muted_role, _, _, _, _ = get_punishment_settings(after.guild.id)
        muted_role = after.guild.get_role(muted_role)

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

            if punishment:
                removed_punishment, success = remove_user_active_punishment(
                    punishment.guild_id,
                    punishment.punishment_id,
                    reason=reason if reason else "No reason provided"
                )

                sent_dm = await send_private_dm(after,
                                                f"Hey! **You're able to chat now!** Please refrain from breaking rules again.")

                await send_punishment_moderation_log(
                    before.guild,
                    after,
                    actioner,
                    removed_punishment,
                    sent_dm,
                    removed=True
                )


async def setup(bot):
    await bot.add_cog(PunishmentEvents(bot))
