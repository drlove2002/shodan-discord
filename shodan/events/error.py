from nextcord import DiscordException, ApplicationError
from nextcord.application_command import Interaction, ApplicationCheckFailure
from nextcord.ext.commands import (
    CommandOnCooldown,
    MissingPermissions,
    BotMissingPermissions,
    Context,
    Cog,
    CommandError,
    ConversionError,
    UserInputError,
    MissingRole,
    CommandInvokeError,
    MaxConcurrencyReached,
)

from shodan.utils.util import Raise, humanize_time

N = "on_command_error"


class ErrorHandler(Cog):
    @Cog.listener(name=N)
    async def missing_perms(self, ctx: Context, error: Exception):
        if not isinstance(error, (MissingPermissions, BotMissingPermissions)):
            return
        missing_perms = ", ".join(error.missing_permissions)
        msg = "You are" if isinstance(error, MissingPermissions) else "I am"
        await Raise(ctx, f"{msg} missing: `{missing_perms}` to run this command").info()

    @Cog.listener(name=N)
    async def concurrency_error(self, ctx: Context, error: Exception):
        if not isinstance(error, MaxConcurrencyReached):
            return
        await Raise(
            ctx,
            f"Someone is already using {ctx.command.name} command! wait until they finish",
        ).info()

    @Cog.listener()
    async def on_application_command_error(self, interaction: Interaction, error: ApplicationError):
        if isinstance(error, ApplicationCheckFailure):
            await Raise(interaction, str(error)).info()
            return

        raise error
    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError):
        try:
            await ctx.message.delete(delay=2)
        except DiscordException:
            pass

        if isinstance(
            error,
            (
                ConversionError,
                UserInputError,
                MissingRole,
            ),
        ):
            await Raise(ctx, str(error)).info()
            ctx.command.reset_cooldown(ctx)
            return
        if hasattr(error, "original") and str(error.original).startswith("[Errno 104]"):
            await Raise(ctx, "I am having trouble connecting to the internet").info()
            ctx.command.reset_cooldown(ctx)
            return

        if not isinstance(error, CommandInvokeError):  # Ignore these errors
            return
        try:
            await ctx.bot.send_log(
                f"{ctx.channel.mention} {ctx.author} \n {str(error.original)}"
            )
        except TypeError:
            pass
        raise error

    @Cog.listener(name=N)
    async def command_on_cooldown(self, ctx: Context, error: Exception):
        if not isinstance(error, CommandOnCooldown):
            return
        # If the command is currently on cooldown trip this
        await Raise(ctx, f"Cooldown: `{humanize_time(error.retry_after)}`").info()


def setup(bot):
    bot.add_cog(ErrorHandler())
