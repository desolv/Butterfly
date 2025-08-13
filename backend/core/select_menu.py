from __future__ import annotations

from typing import Iterable, Callable, Awaitable, Sequence

from discord import Embed, Interaction, SelectOption
from discord.ui import View, Select

from backend.core.helper import get_utc_now


class SelectActionList(View):
    """
    Generic select menu
    """

    def __init__(
            self,
            *,
            author_id: int | None = None,
            embed_title: str,
            embed_description: str | None,
            options: Iterable[SelectOption],
            on_select: Callable[[Interaction, Sequence[str]], Awaitable[None]] | None,
            placeholder: str = "Select an option",
            min_values: int = 1,
            max_values: int = 1,
            disable_after_select: bool = False,
            timeout: float | None = None,
            custom_id: str
    ):
        super().__init__(timeout=timeout)

        self.author_id = author_id
        self.embed_title = embed_title
        self.embed_description = embed_description or ""
        self.on_select = on_select
        self.disable_after_select = disable_after_select

        self.select = Select(
            options=list(options),
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id=custom_id,
        )

        self.add_item(self.select)
        self.select.callback = self.interaction_handler

    def create_embed(self) -> Embed:
        return Embed(
            title=self.embed_title,
            description=self.embed_description,
            color=0x393A41,
            timestamp=get_utc_now(),
        )

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.author_id and interaction.user.id != self.author_id:
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("You can’t use this menu!", ephemeral=True)
            return False

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        return True

    async def interaction_handler(self, interaction: Interaction):
        values = interaction.data.get("values") or []
        if not values:
            await interaction.followup.send("No option selected...", ephemeral=True)
            return

        if self.on_select:
            await self.on_select(interaction, values)

        if self.disable_after_select and self.select.max_values == 1:
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)
