from datetime import datetime

import discord
from discord.ext import commands

from structure.providers.helper import load_json_data, generate_id
from structure.providers.preconditions import has_roles
from structure.repo.models.punishment_model import PunishmentType
from structure.repo.services.punishment_service import create_punishment, deactivate_punishment


class PunishmentCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        punishments = load_json_data(f"environment")["punishments"]
        self.exempt_roles = punishments["exempt_roles"]
        self.exempt_users = punishments["exempt_users"]
        self.moderation_channel = punishments["moderation_channel"]

    def is_exempt(self, member: discord.Member) -> bool:
        if member.id in self.exempt_users:
            return True
        for role in member.roles:
            if role.id in self.exempt_roles:
                return True
        return False

    async def send_moderation_log(self, guild: discord.Guild, embed: discord.Embed):
        channel = guild.get_channel(self.moderation_channel)
        if channel and isinstance(channel, discord.TextChannel):
            await channel.send(embed=embed)

    @has_roles(name="kick", sub="_default")
    @commands.command(
        name="kick",
        description="Kick a member from the server"
    )
    async def _kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.id == ctx.author.id:
            await ctx.send(f"You can't punish your self!")
            return

        if self.is_exempt(member):
            await ctx.send(f"**{member}** is exempt from punishments!")
            return

        await member.kick(reason=reason)
        punishment_id = generate_id()
        create_punishment(punishment_id, member.id, ctx.author.id, PunishmentType.KICK, reason)
        await ctx.send(f"**@{member}** has been kicked for **{reason}**.")

        embed = discord.Embed(
            title=f"ᴋɪᴄᴋ ᴘᴜɴɪѕʜᴍᴇɴᴛ ꜰᴏʀ @{member}",
            description=
            f"**ᴍᴏᴅᴇʀᴀᴛᴏʀ**: {ctx.author.mention}\n"
            f"**ʀᴇᴀѕᴏɴ**: {reason}\n"
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ɪᴅ**: **{punishment_id}**",
            color=discord.Color.yellow(),
            timestamp=datetime.utcnow()
        )

        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=avatar_url)

        await self.send_moderation_log(ctx.guild, embed)


    @has_roles(name="warn", sub="_default")
    @commands.command(
        name="warn",
        description="Warn a member via sending a private message"
    )
    async def _warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.id == ctx.author.id:
            await ctx.send(f"You can't punish your self!")
            return

        if self.is_exempt(member):
            await ctx.send(f"**{member}** is exempt from punishments!")
            return

        await member.send(f"You have been warned by **Staff** for **{reason}**.")
        punishment_id = generate_id()
        create_punishment(punishment_id, member.id, ctx.author.id, PunishmentType.KICK, reason)
        await ctx.send(f"**@{member}** has been warned for **{reason}**.")

        embed = discord.Embed(
            title=f"ᴡᴀʀɴ ᴘᴜɴɪѕʜᴍᴇɴᴛ ꜰᴏʀ @{member}",
            description=
            f"**ᴍᴏᴅᴇʀᴀᴛᴏʀ**: {ctx.author.mention}\n"
            f"**ʀᴇᴀѕᴏɴ**: {reason}\n"
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ɪᴅ**: **{punishment_id}**",
            color=discord.Color.teal(),
            timestamp=datetime.utcnow()
        )

        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=avatar_url)

        await self.send_moderation_log(ctx.guild, embed)


    @has_roles(name="warn", sub="_default")
    @commands.command(
        name="removewarn",
        description="Remove a warning from a member"
    )
    async def _removewarn(self, ctx, member: discord.Member, punishment_id: str, *, reason: str = "No reason provided"):
        if not deactivate_punishment(punishment_id, moderator_id=ctx.author.id):
            await ctx.send(f"Punishment **#{punishment_id}** not found or inactive.")
            return

        await member.send(f"Warning **#{punishment_id}** as been removed by **Staff** for **{reason}**.")
        await ctx.send(f"Warning **#{punishment_id}** has been removed from **@{member}** for **{reason}**.")

        embed = discord.Embed(
            title=f"ᴡᴀʀɴ ʀᴇᴍᴏᴠᴀʟ ꜰᴏʀ @{member}",
            description=
            f"**ᴍᴏᴅᴇʀᴀᴛᴏʀ**: {ctx.author.mention}\n"
            f"**ʀᴇᴀѕᴏɴ**: {reason}\n"
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ɪᴅ**: **{punishment_id}**",
            color=discord.Color.teal(),
            timestamp=datetime.utcnow()
        )

        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=avatar_url)

        await self.send_moderation_log(ctx.guild, embed)





async def setup(bot):
    await bot.add_cog(PunishmentCommandCog(bot))