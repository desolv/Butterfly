import discord
from pyexpat.errors import messages
from sqlalchemy.orm import Session

from discord.ext import commands
from discord import Member
from structure.helper import parse_time_window
from structure.repo.database import engine
from structure.repo.models.relay_model import Relay  # adjust import path
from sqlalchemy import func
from datetime import datetime

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(
        name="relay",
        description="Show user message activity"
    )
    async def _relay(self, ctx, member: Member = None, time_range: str = "1d"):
        try:
            since = parse_time_window(time_range)
        except ValueError as e:
            return await ctx.send(e)
        member = member or ctx.author

        with (Session(engine) as session):
            total = session.query(func.count()).filter(
                Relay.discord_id == member.id,
                Relay.timestamp >= since
            ).scalar()

            deleted = session.query(func.count()).filter(
                Relay.discord_id == member.id,
                Relay.timestamp >= since,
                Relay.is_deleted == True
            ).scalar()

            per_channel = session.query(
                Relay.channel_id,
                func.count().label("count")
            ).filter(
                Relay.discord_id == member.id,
                Relay.timestamp >= since
            ).group_by(Relay.channel_id).order_by(func.count().desc()).limit(3).all()

            global_total = session.query(func.count()).filter(
                Relay.timestamp >= since,
                Relay.discord_id != member.id
            ).scalar()

            user_count = session.query(func.count(func.distinct(Relay.discord_id))).filter(
                Relay.timestamp >= since,
                Relay.discord_id != member.id
            ).scalar()

        if not total:
            return await ctx.send("No relay activity in this time range.")

        days = max((datetime.utcnow() - since).days, 1)
        global_avg_per_user = round(global_total / max(user_count, 1) / days, 1)
        delete_rate = (deleted / total * 100) if total else 0
        per_day = round(total / max((datetime.utcnow() - since).days, 1), 1)
        top_channels = "\n".join(f"<#{cid}> - {count}" for cid, count in per_channel) or "No messages."

        embed = discord.Embed(
            title=f"ʀᴇʟᴀʏ ѕᴛᴀᴛɪѕᴛɪᴄѕ ꜰᴏʀ @{member}",
            description=
            f"**ᴍᴇѕѕᴀɢᴇѕ**: {total}\n"
            f"**ᴅᴇʟᴇᴛᴇᴅ**: {deleted} ({delete_rate:.1f}%)\n",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="ᴀᴠᴇʀᴀɢᴇ/ᴅᴀʏ", value=f"{per_day}", inline=True)
        embed.add_field(name="ᴄᴏᴍᴘᴀʀᴇᴅ ᴛᴏ ɢʟᴏʙᴀʟ ᴀᴠɢ", value=f"{(per_day / global_avg_per_user):.1f}x" if global_avg_per_user > 0 else "N/A", inline=True)
        embed.add_field(name="ᴛɪᴍᴇ ʀᴀɴɢᴇ", value=f"{time_range}", inline=True)
        embed.add_field(name="ᴛᴏᴘ ɪɪɪ ᴄʜᴀɴɴᴇʟѕ", value=f"{top_channels}", inline=False)

        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"@{member}")

        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(
        name="relayboard",
        description="Show leaderboard of message activity"
    )
    async def _relayboard(self, ctx, time_range: str = "1d"):
        try:
            since = parse_time_window(time_range)
        except ValueError as e:
            return await ctx.send(e)

        with Session(engine) as session:
            leaderboard = session.query(
                Relay.discord_id,
                func.count().label("messages"),
                func.sum(func.if_(Relay.is_deleted == True, 1, 0)).label("deleted_messages")
            ).filter(
                Relay.timestamp >= since
            ).group_by(Relay.discord_id).order_by(func.count().desc()).limit(10).all()

        if not leaderboard:
            return await ctx.send("No relay activity in this time range.")


        embed = discord.Embed(
            title=f"ᴛᴏᴘ x ᴜѕᴇʀ - ʀᴇʟᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ꜰᴏʀ {time_range}",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (user_id, messages, deleted) in enumerate(leaderboard, start=1):
            member = ctx.guild.get_member(user_id)
            mention = member if member else f"{user_id}"
            embed.add_field(name=f"@{mention} ᴡɪᴛʜ **{messages} ᴍᴇѕѕᴀɢᴇѕ**", value="", inline=False)

        embed.set_footer(text="Top message senders")

        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(
        name="relaychannels",
        description="Show leaderboard of message activity by channel"
    )
    async def _relaychannels(self, ctx, time_range: str = "1d"):
        try:
            since = parse_time_window(time_range)
        except ValueError as e:
            return await ctx.send(e)

        with Session(engine) as session:
            leaderboard = session.query(
                Relay.channel_id,
                func.count().label("messages"),
                func.sum(func.if_(Relay.is_deleted == True, 1, 0)).label("deleted_messages")
            ).filter(
                Relay.timestamp >= since
            ).group_by(Relay.channel_id).order_by(func.count().desc()).limit(10).all()

        if not leaderboard:
            return await ctx.send("No relay channel activity in this time range.")

        embed = discord.Embed(
            title=f"ᴛᴏᴘ x ᴄʜᴀɴɴᴇʟѕ - ʀᴇʟᴀʏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ꜰᴏʀ {time_range}",
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        for i, (channel_id, messages, deleted) in enumerate(leaderboard, start=1):
            channel = ctx.guild.get_channel(channel_id)
            name = channel.name if channel else f"{channel_id}"
            embed.add_field(name=f"#{name} ᴡɪᴛʜ {messages} ᴍᴇѕѕᴀɢᴇѕ ᴀɴᴅ {deleted or 0} ᴅᴇʟᴇᴛᴇᴅ", value="", inline=False)

        embed.set_footer(text="Top channels activity")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))