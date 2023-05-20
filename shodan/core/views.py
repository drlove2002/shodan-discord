from __future__ import annotations

from typing import Union

from nextcord import (
    ui,
    PartialEmoji,
    Emoji,
    ButtonStyle,
)

class SingleLink(ui.View):
    def __init__(
        self, url: str, label: str = None, emoji: Union[str, PartialEmoji, Emoji] = None
    ):
        super().__init__()
        self.add_item(ui.Button(label=label, url=url, emoji=emoji))

class Vulnerability(ui.Button):

    def __init__(self, ):
        super().__init__(
            style=ButtonStyle.red,
            label="Vulnerabilities",
            emoji="😷",
            custom_id="search-vulnerabilities",
            row=1,
        )
