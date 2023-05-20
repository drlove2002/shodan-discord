from nextcord import DiscordException
from nextcord.ext.commands import Context


async def after_cmd_invoke(ctx: Context):
    """A function that is called after every command invocation."""
    delay = ctx.command.extras.get("delete_delay", 0)
    if not delay:
        return
    try:
        await ctx.message.delete(delay=delay)
    except DiscordException:
        pass
