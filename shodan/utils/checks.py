"""The permission system of the bot is based on a "just works" basis
You have permissions and the bot has permissions. If you meet the permissions
required to execute the command (and the bot does as well) then it goes through
and you can execute the command.
Certain permissions signify if the person is a moderator (Manage Server) or an
admin (Administrator). Having these signify certain bypasses.
Of course, the owner will always be able to execute commands."""
from __future__ import annotations

from typing import TYPE_CHECKING

from nextcord import DMChannel, Message
from nextcord.ext.commands import check

if TYPE_CHECKING:
    from nextcord import TextChannel
    from nextcord.ext.commands import Context


# async def prefix_decider(ctx: Context) -> bool:
#     """Decide prefix for cog."""
#     if ctx.bot.test:
#         return True
#     if ctx.cog.qualified_name == "Mics":
#         return ctx.prefix == "?"
#     return ctx.prefix == "!"


async def check_permissions(ctx: Context, perms, *, checks=all):
    """Checks if the member has permissions to run the command"""
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return checks(
        getattr(resolved, name, None) == value for name, value in perms.items()
    )


def has_permissions(*, checks=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, checks=checks)

    return check(pred)


def is_invoked_with_command(ctx: Context | Message):
    """Check if the command was invoked bt user or from other commands"""
    if isinstance(ctx, Message):
        return False
    return ctx.valid and ctx.invoked_with in (*ctx.command.aliases, ctx.command.name)


async def check_guild_permissions(ctx, perms, *, checks=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return checks(
        getattr(resolved, name, None) == value for name, value in perms.items()
    )


def has_guild_permissions(*, checks=all, **perms):
    async def pred(ctx):
        return await check_guild_permissions(ctx, perms, checks=checks)

    return check(pred)


# These do not take channel overrides into account


def can_bot(perm: str, ctx: Context, channel: TextChannel | None = None) -> bool:
    channel = channel or ctx.channel
    return isinstance(channel, DMChannel) or getattr(
        channel.permissions_for(ctx.guild.me), perm
    )


def can_send(ctx: Context, channel: TextChannel | None = None) -> bool:
    return can_bot("send_messages", ctx, channel)


def can_embed(ctx: Context, channel: TextChannel | None = None) -> bool:
    return can_bot("embed_links", ctx, channel)


def can_upload(ctx: Context, channel: TextChannel | None = None) -> bool:
    return can_bot("attach_files", ctx, channel)


def can_react(ctx: Context, channel: TextChannel | None = None) -> bool:
    return can_bot("add_reactions", ctx, channel)


def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids

    return check(predicate)


def in_dm(ctx: Context):
    return not ctx.guild
