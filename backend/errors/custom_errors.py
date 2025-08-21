from discord.ext import commands


class CustomError(commands.CommandError):
    """
    Base for errors with a clean message.
    """

    def __init__(self, message: str):
        super().__init__(message)


class InvalidURL(CustomError):
    def __init__(self):
        super().__init__(f"Invalid url entered. Please make sure it includes **http/https**!")


class TicketPanelNotFound(CustomError):
    def __init__(self, panel_id: str):
        super().__init__(f"Panel **{panel_id}** not found, or not owned by this guild!")
