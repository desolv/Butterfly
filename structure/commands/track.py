from datetime import datetime

import discord
from discord import Member
from discord.ext import commands
from sqlalchemy import func
from sqlalchemy.orm import Session

from structure.providers.helper import parse_time_window, format_subcommands
from structure.providers.preconditions import has_roles
from structure.repo.database import engine
from structure.repo.models.tracking_model import Track


class TrackCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @has_roles(name="track", sub="_default")
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


    @has_roles(name="track", sub="persona")
    @_track.command(
        name="persona",
        description="Show user message activity"
    )
    async def _track_persona(self, ctx, member: Member = None, duration: str = "1d"):
        try:
            parse_duration = parse_time_window(duration)
        except ValueError as e:
            return await ctx.send(e)
        member = member or ctx.author

        with (Session(engine) as session):
            base_query = session.query(Track).filter(
                Track.user_id == member.id,
                Track.timestamp >= parse_duration
            )

            total = base_query.count()
            deleted = base_query.filter(Track.is_deleted == True).count()

            per_channel = session.query(
                Track.channel_id,
                func.count()
            ).filter(
                Track.user_id == member.id,
                Track.timestamp >= parse_duration
            ).group_by(Track.channel_id).order_by(func.count().desc()).limit(3).all()

            global_total, global_count = session.query(
                func.count(),
                func.count(func.distinct(Track.user_id))
            ).filter(
                Track.timestamp >= parse_duration,
                Track.user_id != member.id
            ).one()

        if not total:
            return await ctx.send("No relay activity in this time range.")

        days = max((datetime.utcnow() - parse_duration).days, 1)
        global_avg_per_persona = round(global_total / max(global_count, 1) / days, 1)
        delete_rate = (deleted / total * 100) if total else 0
        per_day = round(total / max((datetime.utcnow() - parse_duration).days, 1), 1)
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
        embed.add_field(name="ᴛɪᴍᴇ ʀᴀɴɢᴇ", value=f"{duration}", inline=True)
        embed.add_field(name="ᴛᴏᴘ ɪɪɪ ᴄʜᴀɴɴᴇʟѕ", value=f"{top_channels}", inline=False)

        embed.set_thumbnail(url=member.avatar.url)

        await ctx.send(embed=embed)


    @has_roles(name="track", sub="messages")
    @_track.command(
        name="messages",
        description="Show leaderboard of message activity"
    )
    async def _track_messages(self, ctx, duration: str = "1d"):
        try:
            parse_duration = parse_time_window(duration)
        except ValueError as e:
            return await ctx.send(e)

        with Session(engine) as session:
            leaderboard = session.query(
                Track.user_id,
                func.count(),
                func.sum(func.if_(Track.is_deleted == True, 1, 0))
            ).filter(
                Track.timestamp >= parse_duration
            ).group_by(Track.user_id).order_by(func.count().desc()).limit(10).all()

        if not leaderboard:
            return await ctx.send("No relay activity in this time range.")


        embed = discord.Embed(
            title=f"ᴛᴏᴘ x ᴜѕᴇʀ - ᴛʀᴀᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ - {duration}",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (persona_id, messages, deleted) in enumerate(leaderboard, start=1):
            embed.add_field(name=" ", value=f"<@{persona_id}> - **{messages} ᴍᴇѕѕᴀɢᴇѕ**", inline=False)

        await ctx.send(embed=embed)


    @has_roles(name="track", sub="channels")
    @_track.command(
        name="channels",
        description="Show leaderboard of message activity by channel"
    )
    async def _track_channels(self, ctx, duration: str = "1d"):
        try:
            parse_duration = parse_time_window(duration)
        except ValueError as e:
            return await ctx.send(e)

        with Session(engine) as session:
            leaderboard = session.query(
                Track.channel_id,
                func.count(),
                func.sum(func.if_(Track.is_deleted == True, 1, 0))
            ).filter(
                Track.timestamp >= parse_duration
            ).group_by(Track.channel_id).order_by(func.count().desc()).limit(10).all()

        if not leaderboard:
            return await ctx.send("No relay channel activity in this time range.")

        embed = discord.Embed(
            title=f"ᴛᴏᴘ x ᴄʜᴀɴɴᴇʟѕ - ᴛʀᴀᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ - {duration}",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (channel_id, messages, deleted) in enumerate(leaderboard, start=1):
            embed.add_field(name=" ", value=f"<#{channel_id}> - {messages} ᴍᴇѕѕᴀɢᴇѕ ᴀɴᴅ {deleted or 0} ᴅᴇʟᴇᴛᴇᴅ", inline=False)

        await ctx.send(embed=embed)


    @has_roles(name="track", sub="role")
    @_track.command(
        name="role",
        description="Show leaderboard of message activity by role"
    )
    async def _track_role(self, ctx, role: discord.Role, duration: str = "1d"):
        try:
            parse_duration = parse_time_window(duration)
        except ValueError as e:
            return await ctx.send(e)

        members = [m for m in role.members if not m.bot][:50]
        if not members:
            return await ctx.send("No valid members found in that role.")

        with Session(engine) as session:
            persona_ids = [m.id for m in members]
            leaderboard = session.query(
                Track.user_id,
                func.count(),
                func.sum(func.if_(Track.is_deleted == True, 1, 0))
            ).filter(
                Track.user_id.in_(persona_ids),
                Track.timestamp >= parse_duration
            ).group_by(Track.user_id).order_by(func.count().desc()).limit(10).all()

        if not leaderboard:
            return await ctx.send("No relay activity from that role in this time range.")

        embed = discord.Embed(
            title=f"ᴛᴏᴘ @{role.name} ʀᴏʟᴇ - ᴛʀᴀᴄᴋ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ - {duration}",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (persona_id, messages, deleted) in enumerate(leaderboard, start=1):
            embed.add_field(name=" ",  value=f"<@{persona_id}> - **{messages} ᴍᴇѕѕᴀɢᴇѕ**", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TrackCommandCog(bot))