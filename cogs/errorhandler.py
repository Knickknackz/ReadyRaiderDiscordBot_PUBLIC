import discord
from discord.ext import commands


class CommandErrorHandler(commands.Cog):
    """
    This class handles all Command errors
    Was intended to push errors to discord, but
    I Usually have this Disabled.
    Attributes
    ----------
    bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Catches Command errors

        Parameters
        ----------
        ctx
        error
            CommandError child, the error that was raised
        """

        self.bot.log.error(ctx.message.content, exc_info=(type(error), error, error.__traceback__))
        ignored = (commands.CommandNotFound, commands.UserInputError, commands.CheckFailure, commands.CommandOnCooldown)

        # Get original error if exists
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandOnCooldown):
            # await ctx.send(error)
            print(error)
            return

        if isinstance(error, commands.UserInputError):
            # await ctx.send('Error! Please Check Your Formatting: "$help [function name]" ')
            print(error)
            return

        if isinstance(error, (discord.NotFound, discord.Forbidden, discord.HTTPException)):
            print(error)
            return

        if isinstance(error, ignored):
            print(error)
            return
        else:
            print(error)
            return


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
