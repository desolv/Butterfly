import discord
from discord.ext import commands

from backend.voice.director import create_or_update_voice_config, get_voice_by_channel, mark_voice_closed, \
    is_banned, create_voice_channel, has_user_existing_voice_channel
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
                owned_channel = has_user_existing_voice_channel(member)
                if owned_channel is not None:
                    try:
                        await member.move_to(owned_channel)
                    except Exception:
                        pass
                    return

                try:
                    await create_voice_channel(member, config.default_category_id, True)
                except Exception:
                    pass

        if before.channel and before.channel != after.channel:
            try:
                voice = get_voice_by_channel(member.guild.id, before.channel.id)
                if voice and not before.channel.members and voice.is_temporary:
                    await before.channel.delete()
                    mark_voice_closed(before.channel.id)
            except Exception:
                return


async def setup(bot):
    await bot.add_cog(VoiceEvents(bot))
