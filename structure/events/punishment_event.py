import asyncio

import discord
from discord.ext import commands, tasks

from structure.commands.punishment import send_punishment_moderation_log
from structure.providers.helper import load_json_data
from structure.repo.models.punishment_model import PunishmentType
from structure.repo.services.punishment_service import remove_user_active_punishment, \
    get_user_active_punishment, get_global_active_expiring_punishments_within


class PunishmentCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        environment = load_json_data(f"environment")
        self.guild_id = environment["guild_id"]
        self.muted_role_id = environment["punishments"]["muted_role"]
        self.moderation_channel = environment["punishments"]["moderation_channel"]
        self.check_expiring_punishments.start()

    def cog_unload(self):
        self.check_expiring_punishments.cancel()

    @tasks.loop(seconds=30)
    async def check_expiring_punishments(self):
        guild = self.bot.get_guild(self.guild_id)

        for punishment in get_global_active_expiring_punishments_within():
            if not punishment.has_expired():
                continue

            try:
                member = await self.bot.fetch_user(punishment.user_id)
            except Exception:
                print(f"Wasn't able to fetch user {punishment.user_id} for expiring punishments. Aborting!")
                return

            match punishment.type:
                case PunishmentType.MUTE:
                    try:
                        muted_role = guild.get_role(self.muted_role_id)
                        await member.remove_roles(muted_role, reason="Automatic")
                    except Exception:
                        print(f"Wasn't able remove mute for {member}. Aborting!")
                        return

                    sent_dm = await member.send(f"Hey! **You're able to chat now!** Please refrain from breaking rules again.")
                case PunishmentType.BAN:
                    try:
                        await guild.unban(discord.Object(id=punishment.user_id), reason="Automatic")
                    except Exception:
                        print(f"Wasn't able remove ban for {member}. Aborting!")
                        return

                    sent_dm = False
                case _:
                    return

            removed_punishment, success = remove_user_active_punishment(punishment.punishment_id ,reason="Automatic")

            await send_punishment_moderation_log(
                guild,
                member,
                self.bot.user,
                removed_punishment,
                self.moderation_channel,
                sent_dm,
                removed=True
            )


    @check_expiring_punishments.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.guild.id != self.guild_id:
            return

        muted_role = after.guild.get_role(self.muted_role_id)
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

            mute_punishment = get_user_active_punishment(after.id, PunishmentType.MUTE)

            if mute_punishment:
                removed_punishment, success = remove_user_active_punishment(
                    mute_punishment.punishment_id,
                    reason=reason if reason else "No reason provided"
                )

                await send_punishment_moderation_log(
                    before.guild,
                    after,
                    actioner,
                    removed_punishment,
                    self.moderation_channel,
                    False,
                    removed=True
                )

async def setup(bot):
    await bot.add_cog(PunishmentCog(bot))
