import asyncio
import re
from asyncio import TimeoutError
from datetime import timedelta
from typing import NamedTuple

from nextcord import (
    AllowedMentions,
    Colour,
    DiscordException,
    Embed,
    Interaction,
    Message,
    Thread,
)
from nextcord.ext.commands import Context

from shodan.core.constants import ALPHABETS, NORMALIZE_CHARS


async def get_message(
    ctx: Context,
    *,
    content: str = "",
    title=Embed.Empty,
    description=Embed.Empty,
    timeout=100,
    delete_origin=False,
):
    """
    This function sends an embed containing the params and then waits for a message to return
    Params:
     - ctx (context object) : Used for sending msgs n stuff
     - Optional Params:
        - title (string) : Embed title
        - description (string) : Embed description
        - timeout (int) : Timeout for wait_for
    Returns:
     - msg.content (string) : If a message is detected, the content will be returned
     or
     - False (bool) : If a timeout occurs
    """
    embed = Embed(title=title, description=description, color=Colour.dark_theme())
    origin = await ctx.send(content, embed=embed)
    try:
        msg = await ctx.bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if delete_origin:
            await origin.delete()
        if msg:
            return msg.content
    except TimeoutError:
        return False


def clean(message: Message | str) -> str:
    if isinstance(message, Message):
        text = message.content
        for m in set(message.mentions):
            text = text.replace(m.mention, m.display_name)
    else:
        text = message
    unique = [
        i for i in set(text) if i not in ALPHABETS[0]
    ]  # handle special chars from other langs
    for _char in unique:
        try:
            text = text.replace(_char, NORMALIZE_CHARS[_char])
        except KeyError:
            pass
    text = re.sub(
        re.compile(
            r"[\U00003000\U0000205F\U0000202F\U0000200A\U00002000-\U00002009\U00001680\U000000A0\t]+"
        ),
        " ",
        text,
    )  # handle... interesting spaces
    text = re.sub(
        re.compile(r'([.\'"@?!a-z])\1{4,}', re.IGNORECASE), r"\1\1\1", text
    )  # handle excessive repeats of punctuation, limited to 3
    text = re.sub(
        re.compile(r"\s(.+?)\1+\s", re.IGNORECASE), r" \1 ", text
    )  # handle repeated words
    text = re.sub(
        re.compile(r'([\s!?@"\'])\1+'), r"\1", text
    )  # handle excessive spaces or excessive punctuation
    text = re.sub(
        re.compile(r"\s([?.!\"](?:\s|$))"), r"\1", text
    )  # handle spaces before punctuation but after text
    text = text.strip().replace("\n", "/n")  # handle newlines
    text = text.encode("ascii", "ignore").decode()  # remove all non-ascii
    text = text.strip()  # strip the line
    return text


def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content


def code_block(content, lang=""):
    return f"```{lang}\n{content}\n```"

class RaiseType(NamedTuple):
    emoji: str
    color: Colour

def humanize_time(dt: timedelta | float = None):
    """Convert a timedelta or seconds to a human-readable string"""

    def format_data(_time: int, word: str):
        return f"{_time} {word}{'s' if _time > 1 else ''}"

    if dt is None:
        dt = timedelta(seconds=0)
    elif isinstance(dt, (float, int)):
        dt = timedelta(seconds=dt)
    d = dt.days
    m, s = divmod(dt.seconds, 60)
    h, m = divmod(m, 60)
    if int(d):
        return f"{format_data(int(d), 'Day')} {format_data(int(h), 'Hour')}"
    elif int(h):
        return f"{format_data(int(h), 'Hour')} {m} Min"
    elif int(m):
        return f"{m} Min {s} Sec"
    else:
        if s < 1:
            s = dt.total_seconds()
            if s < 0.1:
                return f"{s} Sec"
            else:
                return f"{round(s, 1)} Sec"
        else:
            return f"{int(s)} Sec"



class Raise:
    def __init__(
        self,
        ctx: Context | Interaction | Message,
        message: str,
        *,
        delete_after: int | float | None = 10,
        edit: Message | bool | None = False,
        ephemeral=True,
        view=None,
    ):
        self.ctx = ctx
        self.msg = message
        self.view = view
        self.del_after = delete_after
        self.edit = edit
        self.ephemeral = ephemeral

    async def __response(self, emoji_dict: RaiseType) -> Message | None:
        if isinstance(self.ctx.channel, Thread):
            allowed_mentions = AllowedMentions.none()
        else:
            allowed_mentions = AllowedMentions(
                everyone=False, users=True, roles=False, replied_user=True
            )
        em = Embed(
            color=emoji_dict.color, description=f"{emoji_dict.emoji}**{self.msg}**"
        )
        if isinstance(self.ctx, Interaction):
            if self.edit:
                if not isinstance(self.edit, bool):
                    return await self.edit.edit(embed=em, view=self.view)
                return await self.ctx.edit(embed=em, view=self.view)
            return await self.ctx.send(
                embed=em, ephemeral=self.ephemeral, allowed_mentions=allowed_mentions
            )
        elif isinstance(self.ctx, Message):
            try:
                if self.view is not None:
                    raise DiscordException
                return await self.ctx.reply(
                    embed=em,
                    delete_after=self.del_after,
                    allowed_mentions=allowed_mentions,
                    view=self.view,
                )
            except DiscordException:
                return await self.ctx.channel.send(
                    self.ctx.author.mention,
                    embed=em,
                    delete_after=self.del_after,
                    allowed_mentions=allowed_mentions,
                    view=self.view,
                )
        else:
            if self.edit:
                return await self.edit.edit(
                    content=self.ctx.author.mention,
                    embed=em,
                    view=self.view,
                    allowed_mentions=allowed_mentions,
                )
            try:
                if self.ctx.message.author.bot or self.del_after:
                    raise DiscordException
                return await self.ctx.reply(
                    embed=em, allowed_mentions=allowed_mentions, view=self.view
                )
            except DiscordException:
                return await self.ctx.send(
                    self.ctx.author.mention,
                    embed=em,
                    delete_after=self.del_after,
                    view=self.view,
                    allowed_mentions=allowed_mentions,
                )

    async def error(self) -> Message | None:
        return await self.__response(
            RaiseType("⚠️ ", Colour.red())
        )

    async def info(self) -> Message | None:
        return await self.__response(
            RaiseType("❎ ", Colour.yellow())
        )

    async def success(self) -> Message | None:
        return await self.__response(
            RaiseType("✅ ", Colour.green())
        )

    async def loading(self) -> Message | None:
        return await self.__response(RaiseType("⏳", Colour.blurple()))

    async def custom(self, emoji: str, color: Colour) -> Message | None:
        return await self.__response(RaiseType(emoji, color))

def get_ip() -> str:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return str(s.getsockname()[0])


def call_later_coro(delay, coro, *args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.call_later(delay, asyncio.create_task, coro(*args, **kwargs))
