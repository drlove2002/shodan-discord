from __future__ import annotations

import asyncio
import contextlib
import io
import os
import platform
from textwrap import dedent, indent
from traceback import format_exc
from typing import TYPE_CHECKING

from nextcord import Colour, Embed
from nextcord.application_command import slash_command, Interaction
from nextcord.ext.application_checks import is_owner,bot_has_permissions
from nextcord import __version__ as dpy_v
from nextcord.ext.commands import (
    Cog,
)

from shodan.core.paginator import Paginator
from shodan.utils import logging
from shodan.utils.checks import has_guild_permissions
from shodan.utils.json import upsert_json
from shodan.utils.modules import close, restart
from shodan.utils.util import clean_code

if TYPE_CHECKING:
    from shodan.core.bot import MainBot

logger = logging.get_logger(__name__)


class Developer(Cog):
    r"""Exclusive features for the bot's creator/owner"""

    def __init__(self, bot: MainBot):
        self.bot = bot

    @slash_command(name="setkey")
    @has_guild_permissions(manage_guild=True)
    async def set_api_key(self, inter: Interaction, key: str):
        """Set Shodan API key
        :param inter:
        :parameter key: Shodan API key
        """
        os.environ["SHODAN_KEY"] = key
        self.bot.get_cog("Member")._shodan_key = key
        await inter.send(f"Shodan API key set to ||`{key}`||", ephemeral=True)

    @slash_command()
    async def restart(self, inter: Interaction):
        """Restart the bot"""
        msg = await inter.send(
            embed=Embed(
                color=Colour.brand_red(),
                description=f"***⏳Restarting...***",
            ),
        )

        upsert_json({"restart_msg": msg.id, "restart_channel": msg.channel.id}, "config")
        asyncio.create_task(restart(self.bot))

    @slash_command(name="taskcount")
    @is_owner()
    async def task_count(self, inter: Interaction):
        """
        Return total task count running in background in the bot.
        Use for tracking the load on the bot
        """
        tasks = asyncio.all_tasks()
        filtered_task = [task for task in tasks if not task.done()]
        await inter.send(
            embed=Embed(
                color=Colour.random(),
                title="__Background Tasks__",
                description=dedent(
                    f"""\
                > **Total scheduled tasks: `{len(tasks)}`**

                > **Current running tasks in background: `{len(filtered_task)}`**
                """
                ),
            ),
            ephemeral=True,
        )

    @slash_command(
        name="logout",
        description="Disconnect the bot from discord",
    )
    @is_owner()
    async def logout(self, inter: Interaction):
        await inter.send(f"Hey {inter.user.mention}, I am now logging out :wave:", ephemeral=True)
        await close(self.bot)

    @slash_command()
    @is_owner()
    async def leave(self, inter: Interaction, guild: int):
        """Leave a guild
        :param inter:
        :parameter guild: Guild ID"""
        guild = self.bot.get_guild(guild)
        if not guild:
            return await inter.send("Guild not found", ephemeral=True)
        await guild.leave()
        await inter.send(f":ok_hand: Left guild: {guild.name} ({guild.id})", ephemeral=True)

    @slash_command()
    @bot_has_permissions(embed_links=True)
    @is_owner()
    async def eval(self, inter: Interaction, *, code: str):
        code = clean_code(code)
        local_variables = {
            "Embed": Embed,
            "bot": self.bot,
            "inter": Interaction,
            "channel": inter.channel,
            "author": inter.user,
            "guild": inter.guild,
        }
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(f"async def func():\n{indent(code, '    ')}", local_variables)
                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n-- {obj}\n"
        except (Exception, SyntaxError):
            result = "".join(format_exc())
        pages = [result[i : i + 2000] for i in range(0, len(result), 2000)]
        em = []
        for index, page in enumerate(pages):
            em.append(
                Embed(
                    color=Colour.random(), description=f"```py\n{page}\n```"
                ).set_footer(text=f"Page {index}/{len(pages)}")
            )
        await Paginator(inter, em).start()

    @slash_command(name="botstats")
    @has_guild_permissions(manage_guild=True)
    async def stats_bot(self, inter: Interaction):
        """
        A useful command that displays bot statistics.
        """
        em = Embed(
            title=f"{self.bot.user.name} Stats",
            description="\uFEFF",
            colour=inter.user.color,
        )
        em.add_field(name="Python Version:", value=platform.python_version())
        em.add_field(name="nextcord.Py Version", value=dpy_v)
        em.add_field(name="Total Guilds:", value=str(len(self.bot.guilds)))
        em.add_field(
            name="Total Users:", value=str(len(set(filter(lambda m: not m.bot, self.bot.get_all_members()))))
        )
        em.add_field(name="Bot Developers:", value=f"<@{self.bot.owner_id}>")
        em.set_image(
            url=(
                await self.bot.session.get(
                    "https://source.unsplash.com/random/?server,computer,internet"
                )
            ).url
        )
        em.set_author(name=inter.user.name, icon_url=inter.user.display_avatar.url)

        await inter.send(embed=em, ephemeral=True)

    @slash_command()
    @is_owner()
    async def sync(self, inter: Interaction):
        """Sync all application commands"""
        await self.bot.sync_all_application_commands()
        await inter.send("Synced all application commands", ephemeral=True)

def setup(bot):
    bot.add_cog(Developer(bot))
