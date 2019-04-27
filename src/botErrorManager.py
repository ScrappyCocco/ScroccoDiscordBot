# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import discord


# ---------------------------------------------------------------------


class BotErrorManager(commands.Cog):
    """ Class with Bot Errors Manager, when an error happen, on_command_error(...) is called """

    # ---------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_command_error(self, error, ctx):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception
        """
        ignored = (commands.CommandNotFound, commands.CommandOnCooldown)
        message_channel: discord.abc.Messageable = error.channel

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            print("Error manager: Error ignored (Type:" + str(type(error)) + ")")
            return
        # An error occurred invoking the command
        elif isinstance(error, commands.CommandInvokeError):
            print("Error manager: Sending message for CommandInvokeError")
            return await message_channel.send(":middle_finger: *An error occurred invoking the command...*")
        # There are an error with command Arguments
        elif isinstance(error, commands.BadArgument):
            print("Error manager: Sending message for BadArgument")
            return await message_channel.send(
                ":middle_finger: *Looks like there is a problem with command arguments, please check command usage...*")
        else:  # No Error Manager, print error to bot log
            if hasattr(ctx, 'original'):
                error_message = str(ctx.original)
            elif hasattr(ctx, 'args'):
                error_message = str(ctx.args)
            else:
                error_message = str(ctx)
            print(
                "Error manager - ERROR: No error control detected, error:\"" + error_message + "\" - Command invoked:" + str(
                    error.invoked_with) + " - (Error Type:" + str(type(error)) + ")")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING ERROR MANAGER CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot
        print("Error manager: Error manager ready")

    def __del__(self):
        print("DESTROYING ERROR MANAGER CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotErrorManager(bot))
