from __future__ import annotations

import os
import subprocess
from asyncio import create_task
from pathlib import Path
from typing import TYPE_CHECKING

from nextcord import (
    Activity,
    ActivityType,
    Colour,
    Embed,
    Status,
)
from nextcord.ext.commands import ExtensionAlreadyLoaded

from shodan.utils import logging
from shodan.utils.json import read_json, write_json

if TYPE_CHECKING:
    from shodan.core.bot import MainBot


logger = logging.get_logger(__name__)
ROOT_DIR = str(Path(__file__).parents[1])


def run_command(command: str) -> str:
    process = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, text=True, shell=True
    )
    process.wait()
    output = process.communicate()[0]
    return output


async def restart(bot: MainBot) -> None:
    logger.line()
    await bot.change_presence(
        status=Status.idle,
        activity=Activity(type=ActivityType.watching, name="and Restarting...⚠️"),
    )
    run_command(f"python3 restart.py {os.getpid()}")
    logger.info("↻ Restarting bot...")
    await close(bot)


async def close(bot: MainBot) -> None:
    """Close the bot gracefully"""
    import asyncio

    # Cancel all tasks
    for task in asyncio.all_tasks():
        task.cancel("Bot is logging out")
    await bot.session.close()
    await bot.close()
    bot.db.close()
    await bot.sql.close()
    bot.loop.stop()


async def post_restart(bot: MainBot) -> None:
    import signal

    # Load restart configs from config.json
    data = read_json("config")
    if "restart_msg" in data:
        msg = await bot.get_channel(
            int(data.pop("restart_channel"))
        ).fetch_message(int(data.pop("restart_msg")))
        create_task(
            msg.edit(
                embed=Embed(
                    color=Colour.green(),
                    description="***✅Restarted!***",
                )
            )
        )
        write_json(data, "config")

    # Add signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        bot.loop.remove_signal_handler(sig)
        bot.loop.add_signal_handler(sig, lambda: create_task(close(bot)))

    bot.guild = bot.get_guild(bot.default_guild_ids[0])

def load_cogs(bot: MainBot) -> None:
    """Add all cogs to the bot."""
    for file in os.listdir(ROOT_DIR + "/cogs"):
        if file.startswith("_"):
            continue
        try:
            if os.path.isdir(ROOT_DIR + "/cogs" + f"/{file}"):
                bot.load_extension(f"shodan.cogs.{file}.main")
            else:
                file = file[:-3]
                bot.load_extension(f"shodan.cogs.{file}")
        except ExtensionAlreadyLoaded:
            pass
        logger.info("✅ %s cog loaded", file.capitalize())
    logger.line()


def load_events(bot: MainBot) -> None:
    """Add event handlers to the bot"""
    for file in os.listdir(ROOT_DIR + "/events"):
        if file.startswith("_"):
            continue
        try:
            bot.load_extension(f"shodan.events.{file[:-3]}")
        except ExtensionAlreadyLoaded:
            pass
