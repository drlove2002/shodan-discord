from __future__ import annotations

import io
from datetime import datetime
from os import getenv
from json import JSONDecodeError
from typing import TYPE_CHECKING

from aiohttp import ClientResponseError
from nextcord import (
    Colour,
    Embed,
    Forbidden,
    Member,
    File,
    ui,
)
from nextcord.application_command import (
    slash_command,
    Interaction,
    ApplicationCommandType,
    Range,
)
from nextcord.ext.commands import (
    Cog,
)

from shodan.core.paginator import PaginatorView
from shodan.core.views import Vulnerability
from shodan.utils.logging import get_logger
from shodan.utils.util import Raise, code_block

if TYPE_CHECKING:
    from shodan.core.bot import MainBot

logger = get_logger(__name__)


class Member(Cog):
    """Commands related to members"""

    def __init__(self, bot: MainBot):
        self.bot = bot
        self.session = bot.session
        self._shodan_key = getenv("SHODAN_KEY")

    @slash_command()
    async def ping(self, inter: Interaction):
        """Ping me to see how fast I can respond!"""
        await inter.send(f"> Pong! `{round(self.bot.latency * 1000)}ms`")

    @slash_command()
    async def search(self, inter: Interaction, query: str, facets: str = None, page: Range[1, 100] = 1):
        """Do Shodan search

        Parameters
        ----------
        inter:
        query: str
            Shodan search query
        facets: Optional[str]
            A comma-separated list of properties to get summary information on
        page: Optional[int]
            The page number to page through results 100 at a time
        """
        if not self._shodan_key:
            cmd = self.bot.get_application_command_from_signature(
                "setkey",
                ApplicationCommandType.chat_input,
                inter.guild_id
            )
            return await Raise(inter, f"First set SHODAN_API_KEY via {cmd.get_mention(inter.guild)} command").error() # noqa

        msg = await inter.send(
            embed=Embed(
                color=Colour.brand_red(),
                description=f"***⏳Searching...***",
            ),
        )

        try:
            perms = {"key": self._shodan_key, "query": query, "page": page}
            if facets:
                perms["facets"] = facets
            results = await self.session.get(
                "https://api.shodan.io/shodan/host/search",
                params=perms,
            )
            results = await results.json()
        except JSONDecodeError:
            return await Raise(inter, "Invalid JSON response from Shodan API",  edit=msg).error()
        except Forbidden as e:
            return await Raise(inter, f"[Status-{e.status}] {e.text}", edit=msg).error()
        except ClientResponseError  as e:
            return await Raise(inter, f"[Status-{e.status}]  {e.message}", edit=msg).error()

        if not results["matches"]:
            return await Raise(inter, "No results found", edit=msg).error()

        embeds = []
        for match in results["matches"]:
            embed = Embed(
                title=match["org"],
                color=Colour.random(seed=match['ip_str']),
                url=f"https://www.shodan.io/host/{match['ip_str']}",
                timestamp=datetime.fromisoformat(match["timestamp"]) if match["timestamp"] else None,
            ).add_field(
                name="🌐 IP-Address",
                value=code_block(f"{match['ip_str']}:{match['port']}", "rb"),
                inline=False,
            ).set_author(
                name=f"Location: {match['location']['city']}, {match['location']['country_name']}",
                url=f"https://www.google.com/maps/search/"
                    f"{match['location']['latitude']},{match['location']['longitude']}",
                icon_url="https://cdn-icons-png.flaticon.com/512/2875/2875433.png",
            ).set_footer(text=f"Total Pages: {results['total']}")

            if match["hostnames"]:
                embed.add_field(
                    name="📛 Hostnames",
                    value=code_block("\n".join(match["hostnames"]), "py"),
                    inline=False,
                )

            embeds.append(embed)

        view = PaginatorView(inter.user, embeds)
        vulnerability = Vulnerability()
        view.add_item(vulnerability)

        async def vulnerability_callback(interaction: Interaction):
            """Callback for vulnerability button"""
            await interaction.send(embed=Embed(description="***⏳Searching...***"), ephemeral=True)
            ems = []
            for cve, data in results["matches"][view.index]["vulns"].items():
                ems.append(Embed(
                    title=cve,
                    color=Colour.random(seed=cve),
                    description=data["summary"],
                    url=data["references"][0],
                ).add_field(
                    name="🎚 CVSS",
                    value=code_block(data["cvss"]),
                ).add_field(
                    name="Verified",
                    value=code_block(data["verified"]),
                ))
            vuln_view = PaginatorView(interaction.user, ems)

            async def _callback(_):
                for item in vuln_view.children:
                    if isinstance(item, ui.Button) and item.custom_id == "page_count":
                        item.label = f"Page {vuln_view.index + 1}/{len(ems)}"

                await interaction.edit_original_message(embed=ems[vuln_view.index], view=vuln_view)
            vuln_view.button_callback = _callback

            await _callback(None)



        vulnerability.callback = vulnerability_callback

        async def button_callback(_):
            match_result = results["matches"][view.index]
            for item in view.children:
                item: ui.Button
                if item.custom_id == "page_count":
                    item.label = f"Page {view.index + 1}/{len(view.embeds)}"
                if item.custom_id == "search-vulnerabilities":
                    if "vulns" in match_result and match_result["vulns"]:
                        item.disabled = False
                    else:
                        item.disabled = True

            if "http" in results["matches"][view.index]:
                headers = io.BytesIO(results["matches"][view.index]["data"].split("\r\n\r\n")[0].encode("utf-8"))
                files = [File(fp=headers, filename="headers.txt")]
                if "html" in match_result["http"]:
                    files.append(File(fp=io.BytesIO(match_result["http"]["html"].encode("utf-8")), filename="page.html"))
            elif "data" in results["matches"][view.index]:
                files = [File(fp=io.BytesIO(results["matches"][view.index]["data"].encode("utf-8")), filename="data.txt")]
            else:
                files = None
            await view.msg.edit(embed=embeds[view.index], view=view, files=files)

        view.button_callback = button_callback
        view.msg = msg

        await button_callback(None)


def setup(bot: MainBot):
    bot.add_cog(Member(bot))
