from discord.ext import commands

from backend.core.helper import get_commands_help_messages
from backend.core.pagination import Pagination
from backend.permissions.commands.permission_admin import PermissionAdminCommand
from backend.permissions.enforce import has_permission, has_cooldown
from backend.punishments.commands.ban import BanCommand
from backend.punishments.commands.kick import KickCommand
from backend.punishments.commands.mute import MuteCommand
from backend.punishments.commands.punishment import PunishmentCommand
from backend.punishments.commands.punishment_admin import PunishmentAdminCommand
from backend.punishments.commands.warn import WarnCommand
from backend.tickets.commands.ticket import TicketCommand
from backend.tickets.commands.ticket_admin import TicketAdminCommand


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @has_cooldown()
    @commands.group(name="help", invoke_without_command=True)
    async def _help(self, ctx):
        view = Pagination(
            "ʜᴇʟᴘ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(self.bot, [HelpCommand], ctx.author.guild_permissions.administrator),
            3,
            ctx.author.id
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @has_cooldown()
    @_help.command(name="moderation")
    async def _help_moderation(self, ctx):
        """
        Get moderation related commands listing
        """
        view = Pagination(
            "ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(
                self.bot,
                [BanCommand, KickCommand, MuteCommand, WarnCommand, PunishmentCommand, TicketCommand],
                ctx.author.guild_permissions.administrator
            ),
            5,
            ctx.author.id
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @has_cooldown()
    @_help.command(name="management")
    async def _help_management(self, ctx):
        """
        Get management related commands listing
        """
        view = Pagination(
            "ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(
                self.bot,
                [PunishmentAdminCommand, PermissionAdminCommand, TicketAdminCommand],
                ctx.author.guild_permissions.administrator
            ),
            5,
            ctx.author.id
        )

        await ctx.reply(embed=view.create_embed(), view=view)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
