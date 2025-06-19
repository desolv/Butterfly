import discord
from sqlalchemy.orm import Session

from discord.ext import commands
from discord import Member
from structure.helper import parse_time_window
from structure.repo.database import engine
from structure.repo.models.logbook_model import Logbook  # adjust import path
from sqlalchemy import func
from datetime import datetime

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(
        name="logbook",
        description="Show user message statistics"
    )
    async def _logbook(self, ctx, member: Member = None, time_range: str = "1d"):
        try:
            since = parse_time_window(time_range)
        except ValueError as e:
            return await ctx.send(e)
        member = member or ctx.author

        with (Session(engine) as session):
            total = session.query(func.count()).filter(
                Logbook.discord_id == member.id,
                Logbook.timestamp >= since
            ).scalar()

            deleted = session.query(func.count()).filter(
                Logbook.discord_id == member.id,
                Logbook.timestamp >= since,
                Logbook.is_deleted == True
            ).scalar()

            per_channel = session.query(
                Logbook.channel_id,
                func.count().label("count")
            ).filter(
                Logbook.discord_id == member.id,
                Logbook.timestamp >= since
            ).group_by(Logbook.channel_id).order_by(func.count().desc()).limit(3).all()

            global_total = session.query(func.count()).filter(
                Logbook.timestamp >= since,
                Logbook.discord_id != member.id
            ).scalar()

            user_count = session.query(func.count(func.distinct(Logbook.discord_id))).filter(
                Logbook.timestamp >= since,
                Logbook.discord_id != member.id
            ).scalar()

        days = max((datetime.utcnow() - since).days, 1)
        global_avg_per_user = round(global_total / max(user_count, 1) / days, 1)
        delete_rate = (deleted / total * 100) if total else 0
        per_day = round(total / max((datetime.utcnow() - since).days, 1), 1)
        top_channels = "\n".join(f"<#{cid}> - {count}" for cid, count in per_channel) or "No messages."

        embed = discord.Embed(
            title=f"ʟᴏɢʙᴏᴏᴋ ѕᴛᴀᴛɪѕᴛɪᴄѕ ꜰᴏʀ @{member}",
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

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))