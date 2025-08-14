from discord import Embed, Interaction, ButtonStyle
from discord.ui import View, Button

from backend.core.helper import get_time_now


def chunk_lines(lines: list[str], size: int) -> list[str]:
    return [
        "\n".join(lines[i:i + size])
        for i in range(0, len(lines), size)
    ]


def chunk_as_fields(lines: list[str], size: int) -> list[list[str]]:
    """
    Return pages where each page is a list of lines
    """
    return [
        lines[i:i + size]
        for i in range(0, len(lines), size)
    ]


class Pagination(View):
    def __init__(
            self,
            title: str,
            lines: list[str],
            lines_per_page: int,
            author_id: int,
            is_field: bool = False
    ):
        super().__init__(timeout=180)
        self.title = title
        self.is_field = is_field

        if self.is_field:
            lines_per_page = min(lines_per_page, 25)

        self.pages = (
            chunk_as_fields(lines, lines_per_page)
            if self.is_field else
            chunk_lines(lines, lines_per_page)
        )
        self.page = 0
        self.author_id = author_id
        self.build_buttons()

    def create_embed(self) -> Embed:
        embed = Embed(
            title=self.title,
            color=0x393A41,
            timestamp=get_time_now()
        ).set_footer(text=f"{self.page + 1}/{len(self.pages)}")

        if not self.is_field:
            embed.description = self.pages[self.page] if self.pages else ""
            return embed

        current = self.pages[self.page] if self.pages else []
        for line in current:
            embed.add_field(name="", value=line, inline=True)
        return embed

    def build_buttons(self):
        self.clear_items()

        if len(self.pages) <= 1:
            return

        if self.page > 0:
            self.add_item(Button(label="⏮️", style=ButtonStyle.grey, custom_id="first"))

        self.add_item(Button(label="◀️", style=ButtonStyle.blurple, custom_id="prev"))
        self.add_item(Button(label="▶️", style=ButtonStyle.blurple, custom_id="next"))

        if self.page < len(self.pages) - 1:
            self.add_item(Button(label="⏭️", style=ButtonStyle.grey, custom_id="last"))

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.followup.send("You are not allowed to use this!", ephemeral=True)
            return False

        if not interaction.response.is_done():
            await interaction.response.defer()

        await self.interaction_handler(interaction)
        return True

    async def interaction_handler(self, interaction: Interaction):
        match interaction.data["custom_id"]:
            case "first":
                self.page = 0
            case "prev":
                if self.page > 0:
                    self.page -= 1
            case "next":
                if self.page < len(self.pages) - 1:
                    self.page += 1
            case "last":
                self.page = len(self.pages) - 1

        self.build_buttons()
        await interaction.message.edit(embed=self.create_embed(), view=self)
