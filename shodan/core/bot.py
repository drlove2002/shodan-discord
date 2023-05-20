# Standard libraries
import os
from pathlib import Path
from typing import TypeVar

# Third party libraries
import aiohttp

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ImportError:
    pass
from nextcord import Activity, ActivityType, Guild, Intents, Status
from nextcord import __version__ as dpy_v
from nextcord.ext.commands import Bot, ExtensionAlreadyLoaded

# Local code
from shodan import __version__

from ..events._helper import after_cmd_invoke
from ..utils import logging
from ..utils.modules import load_cogs, load_events, post_restart

ROOT_DIR = str(Path(__file__).parents[1])
logger = logging.get_logger(__name__)
logger.info(f"{ROOT_DIR}\n-----")

__all__ = ("BaseMainBot", "MainBot")


class BaseMainBot(Bot):
    def __init__(self):
        super().__init__(
            intents=Intents._from_value(4611),
            case_insensitive=True,
            owner_id=506498413857341440,
            strip_after_prefix=True,
            status=Status.online,
            activity=Activity(type=ActivityType.watching, name="the Internet🌐..."),
            default_guild_ids=[802729029236031548],
        )
        # Defining a few things
        self.test: bool = os.getenv("TEST", "False").lower() in ("1", "true", "T")
        self.guild: Guild | None = None
        self.session = aiohttp.ClientSession(trust_env=True)
        self.after_invoke(after_cmd_invoke)

    @property
    def member(self):
        """Returns the bot's member object."""
        return self.guild.get_member(self.user.id)

    async def on_ready(self):
        """Called when the bot is ready."""
        await self.wait_until_ready()
        await post_restart(self)

        logger.line()
        logger.info("Nextcord.py: v%s", dpy_v)
        logger.info("Bot Version: %s", __version__)
        logger.line()

        # Add cogs to the bot
        load_cogs(self)

        if self.test:
            try:
                self.load_extension("mainbot.events.error")
            except ExtensionAlreadyLoaded:
                pass
            return

        await self.sync_all_application_commands()
        logger.info("Synced all application commands")
        load_events(self)
        logger.info(f"{len(self.persistent_views)} view(s) are added")

        logger.info(f"Logged in as: {self.user.name} : {self.user.id}")

    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        await self.process_commands(message)

    # async def get_prefix(self, message) -> list[str]:
    #     return when_mentioned_or("$" if self.test else "shodan")(self, message)


MainBot = TypeVar("MainBot", bound=BaseMainBot)
"MainBot will be used only for typehints of BaseMainBot"
