from datetime import datetime

import discord
from discord import Member
from discord.ext import commands
from sqlalchemy import func
from sqlalchemy.orm import Session

from structure.providers.helper import parse_time_window, format_subcommands
from structure.providers.preconditions import has_roles
from structure.repo.database import engine
from structure.repo.models.relay_model import Relay


class TrackCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @has_roles(group="track", sub="_default")
    @commands.group(
        name="track",
        invoke_without_command=True
    )
    async def _track(self, ctx):
        lines = format_subcommands(self.bot, "track")

        embed = discord.Embed(
            title="ᴛʀᴀᴄᴋ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            description="\n".join(lines),
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        await ctx.send(embed=embed)


    @has_roles(group="track", sub="persona")
    @_track.command(
        name="persona",
        description="Show user message activity"
    )
    async def _track_persona(self, ctx, member: Member = None, time_range: str = "1d"):
        try:
            since = parse_time_window(time_range)
        except ValueError as e:
            return await ctx.send(e)
        member = member or ctx.author

        with (Session(engine) as session):
            base_query = session.query(Relay).filter(
                Relay.discord_id == member.id,
                Relay.timestamp >= since
            )

            total = base_query.count()
            deleted = base_query.filter(Relay.is_deleted == True).count()

            per_channel = session.query(
                Relay.channel_id,
                func.count()
            ).filter(
                Relay.discord_id == member.id,
                Relay.timestamp >= since
            ).group_by(Relay.channel_id).order_by(func.count().desc()).limit(3).all()

            global_total, global_count = session.query(
                func.count(),
                func.count(func.distinct(Relay.discord_id))
            ).filter(
                Relay.timestamp >= since,
                Relay.discord_id != member.id
            ).one()

        if not total:
            return await ctx.send("No relay activity in this time range.")

        days = max((datetime.utcnow() - since).days, 1)
        global_avg_per_persona = round(global_total / max(global_count, 1) / days, 1)
        delete_rate = (deleted / total * 100) if total else 0
        per_day = round(total / max((datetime.utcnow() - since).days, 1), 1)
        top_channels = "\n".join(f"<#{cid}> - {count}" for cid, count in per_channel) or "No messages."

        embed = discord.Embed(
            title=f"ᴛʀᴀᴄᴋ ѕᴛᴀᴛɪѕᴛɪᴄѕ ꜰᴏʀ @{member}",
            description=
            f"**ᴍᴇѕѕᴀɢᴇѕ**: {total}\n"
            f"**ᴅᴇʟᴇᴛᴇᴅ**: {deleted} ({delete_rate:.1f}%)\n",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="ᴀᴠᴇʀᴀɢᴇ/ᴅᴀʏ", value=f"{per_day}", inline=True)
        embed.add_field(name="ᴄᴏᴍᴘᴀʀᴇᴅ ᴛᴏ ɢʟᴏʙᴀʟ ᴀᴠɢ", value=f"{(per_day / global_avg_per_persona):.1f}x" if global_avg_per_persona > 0 else "N/A", inline=True)
        embed.add_field(name="ᴛɪᴍᴇ ʀᴀɴɢᴇ", value=f"{time_range}", inline=True)
        embed.add_field(name="ᴛᴏᴘ ɪɪɪ ᴄʜᴀɴɴᴇʟѕ", value=f"{top_channels}", inline=False)

        embed.set_thumbnail(url=member.avatar.url)

        await ctx.send(embed=embed)


    @has_roles(group="track", sub="messages")
    @_track.command(
        name="messages",
        description="Show leaderboard of message activity"
    )
    async def _track_messages(self, ctx, time_range: str = "1d"):
        try:
            since = parse_time_window(time_range)
        except ValueError as e:
            return await ctx.send(e)

        with Session(engine) as session:
            leaderboard = session.query(
                Relay.discord_id,
                func.count(),
                func.sum(func.if_(Relay.is_deleted == True, 1, 0))
            ).filter(
                Relay.timestamp >= since
            ).group_by(Relay.discord_id).order_by(func.count().desc()).limit(10).all()

        if not leaderboard:
            return await ctx.send("No relay activity in this time range.")


        embed = discord.Embed(
            title=f"ᴛᴏᴘ x ᴜѕᴇʀ - ᴛʀᴀᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ - {time_range}",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (persona_id, messages, deleted) in enumerate(leaderboard, start=1):
            member = ctx.guild.get_member(persona_id)
            embed.add_field(name=" ", value=f"{member.mention} - **{messages} ᴍᴇѕѕᴀɢᴇѕ**", inline=False)

        await ctx.send(embed=embed)


    @has_roles(group="track", sub="channels")
    @_track.command(
        name="channels",
        description="Show leaderboard of message activity by channel"
    )
    async def _track_channels(self, ctx, time_range: str = "1d"):
        try:
            since = parse_time_window(time_range)
        except ValueError as e:
            return await ctx.send(e)

        with Session(engine) as session:
            leaderboard = session.query(
                Relay.channel_id,
                func.count(),
                func.sum(func.if_(Relay.is_deleted == True, 1, 0))
            ).filter(
                Relay.timestamp >= since
            ).group_by(Relay.channel_id).order_by(func.count().desc()).limit(10).all()

        if not leaderboard:
            return await ctx.send("No relay channel activity in this time range.")

        embed = discord.Embed(
            title=f"ᴛᴏᴘ x ᴄʜᴀɴɴᴇʟѕ - ᴛʀᴀᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ - {time_range}",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (channel_id, messages, deleted) in enumerate(leaderboard, start=1):
            channel = ctx.guild.get_channel(channel_id)
            embed.add_field(name=" ", value=f"{channel.mention} - {messages} ᴍᴇѕѕᴀɢᴇѕ ᴀɴᴅ {deleted or 0} ᴅᴇʟᴇᴛᴇᴅ", inline=False)

        await ctx.send(embed=embed)


    @has_roles(group="track", sub="role")
    @_track.command(
        name="role",
        description="Show leaderboard of message activity by role"
    )
    async def _track_role(self, ctx, role: discord.Role, time_range: str = "1d"):
        try:
            since = parse_time_window(time_range)
        except ValueError as e:
            return await ctx.send(e)

        members = [m for m in role.members if not m.bot][:50]
        if not members:
            return await ctx.send("No valid members found in that role.")

        with Session(engine) as session:
            persona_ids = [m.id for m in members]
            leaderboard = session.query(
                Relay.discord_id,
                func.count(),
                func.sum(func.if_(Relay.is_deleted == True, 1, 0))
            ).filter(
                Relay.discord_id.in_(persona_ids),
                Relay.timestamp >= since
            ).group_by(Relay.discord_id).order_by(func.count().desc()).limit(10).all()

        if not leaderboard:
            return await ctx.send("No relay activity from that role in this time range.")

        embed = discord.Embed(
            title=f"ᴛᴏᴘ @{role.name} ʀᴏʟᴇ - ᴛʀᴀᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ - {time_range}",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (persona_id, messages, deleted) in enumerate(leaderboard, start=1):
            member = ctx.guild.get_member(persona_id)
            embed.add_field(name=" ",  value=f"{member.mention} - **{messages} ᴍᴇѕѕᴀɢᴇѕ**", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TrackCommandCog(bot))