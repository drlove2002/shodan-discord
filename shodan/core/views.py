from __future__ import annotations

from asyncio import create_task

from typing import Union, Optional, TYPE_CHECKING

from nextcord import (
    ui,
    PartialEmoji,
    Emoji,
    Message,
    Interaction,
    ButtonStyle,
    Colour,
    Embed,
    Member,
)
from nextcord.ext.commands import Context

from shodan.utils.util import Raise

if TYPE_CHECKING:
    from .bot import MainBot


class SingleLink(ui.View):
    def __init__(
        self, url: str, label: str = None, emoji: Union[str, PartialEmoji, Emoji] = None
    ):
        super().__init__()
        self.add_item(ui.Button(label=label, url=url, emoji=emoji))

class CoinFlip(ui.View):
    children: list[ui.Button]

    def __init__(self, ctx: Context):
        super().__init__(timeout=30)
        self.msg: Optional[Message] = None
        self.ctx = ctx
        self.choice = None

    async def interaction_check(self, interaction: Interaction) -> bool:
        await self.msg.delete()
        if interaction.guild is None or (
            interaction.channel_id == self.ctx.channel.id
            and self.ctx.author.id == interaction.user.id
        ):
            return True
        await Raise(interaction, "You can't use this button").error()
        return False

    async def on_timeout(self) -> None:
        for child in self.children:
            if not child.disabled:
                child.disabled = True
        await self.msg.edit(view=self)

    @ui.button(emoji="💀", label="HEAD", style=ButtonStyle.blurple)
    async def head(self, button: ui.Button, inter: Interaction):
        await inter.response.defer()
        self.choice = button.label[0]
        self.stop()

    @ui.button(
        emoji="<a:FoxxoTailwag:809905990530105385>",
        label="TAIL",
        style=ButtonStyle.blurple,
    )
    async def tail(self, button: ui.Button, inter: Interaction):
        await inter.response.defer()
        self.choice = button.label[0]
        self.stop()
