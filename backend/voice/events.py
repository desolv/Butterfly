import discord
from discord.ext import commands

from backend.voice.director import create_or_update_voice_config, create_voice, get_voice_by_channel, delete_voice, \
    is_banned, get_user_active_voice
from backend.voice.ui.voice_views import VoiceViews


class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(VoiceViews())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if after.channel and after.channel != before.channel:
            config = create_or_update_voice_config(member.guild.id)
            if not config.is_enabled or is_banned(member, config):
                return

            if config.join_channel_id and after.channel.id == config.join_channel_id:
                owned = get_user_active_voice(member.guild.id, member.id)
                if owned:
                    existing_channel = member.guild.get_channel(owned.channel_id)
                    if existing_channel:
                        try:
                            await member.move_to(existing_channel)
                        except discord.HTTPException:
                            pass
                        return
                    delete_voice(owned.channel_id)
                    return

                try:
                    category = member.guild.get_channel(config.category_id)
                    created_channel = await member.guild.create_voice_channel(
                        name=f"{member.display_name}'s",
                        category=category
                    )
                    await member.move_to(created_channel)
                    create_voice(member.guild.id, member.id, created_channel.id)
                except Exception:
                    return

        if before.channel and before.channel != after.channel:
            try:
                voice = get_voice_by_channel(member.guild.id, before.channel.id)
                if voice and not before.channel.members:
                    await before.channel.delete()
                    delete_voice(before.channel.id)
            except Exception:
                return


async def setup(bot):
    await bot.add_cog(VoiceEvents(bot))
