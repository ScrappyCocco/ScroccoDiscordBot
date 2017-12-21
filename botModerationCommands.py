# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import discord

from botMethodsClass import BotMethods


# ---------------------------------------------------------------------


class BotModerationCommands:
    """ Class with Bot 'Moderation' commands (for example ban and kick users) """

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def banuser(self, ctx):
        """Function that ban a user from the server
        Usage: !banuser @User
        """
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await self.bot.send_message(ctx.message.channel, "Error with mentions...")
                return
            print("-------------------------")
            try:
                await self.bot.ban(ctx.message.mentions[0], delete_message_days=100)
                await self.bot.send_message(ctx.message.channel, str(ctx.message.mentions[0].name) + " has been banned")
            except discord.errors.Forbidden:
                await self.bot.send_message(ctx.message.channel, "Sorry, I don't have the `ban` permission")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def unbanuser(self, ctx):
        """Function that un-ban a user from the server
        Usage: !unbanuser @User
        """
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await self.bot.send_message(ctx.message.channel, "Error with mentions...")
                return
            print("-------------------------")
            try:
                await self.bot.unban(ctx.message.server, ctx.message.mentions[0])
                await self.bot.send_message(ctx.message.channel,
                                            str(ctx.message.mentions[0].name) + " has been un-banned")
            except discord.errors.Forbidden:
                await self.bot.send_message(ctx.message.channel, "Sorry, I don't have the `ban` permission")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def softban(self, ctx):
        """Function that soft-ban (=ban and unban deleting the messages) a user from the server
        Usage: !softban @User
        """
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await self.bot.send_message(ctx.message.channel, "Error with mentions...")
                return
            print("-------------------------")
            try:
                await self.bot.ban(ctx.message.mentions[0], delete_message_days=100)
                await self.bot.unban(ctx.message.server, ctx.message.mentions[0])
                await self.bot.send_message(ctx.message.channel,
                                            str(ctx.message.mentions[0].name) + " has been soft-banned ")
            except discord.errors.Forbidden:
                await self.bot.send_message(ctx.message.channel, "Sorry, I don't have the `softban` permission")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def kickuser(self, ctx):
        """Function that kick a user from the server
        Usage: !kickuser @User
        """
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await self.bot.send_message(ctx.message.channel, "Error with mentions...")
                return
            print("-------------------------")
            try:
                await self.bot.kick(ctx.message.mentions[0])
                await self.bot.send_message(ctx.message.channel, str(ctx.message.mentions[0].name) + " has been kicked")
            except discord.errors.Forbidden:
                await self.bot.send_message(ctx.message.channel, "Sorry, I don't have the `kick` permission")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def editallroles(self, ctx, *args):
        """Function that change the role of ALL users (add/remove a role)
        USE WITH CAUTION
        Usage: !editallroles remove "NoobRole"
        Usage: !editallroles add "ProRole"
        """
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't edit roles in private, execute the command in a server*")
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 2:
                await self.bot.send_message(ctx.message.channel, "Parameters not correct...")
                return
            print("-------------------------")
            server_members = ctx.message.server.members
            action = str(args[0])
            selected_role = discord.utils.get(ctx.message.server.roles, name=str(args[1]))
            if selected_role is None:
                await self.bot.send_message(ctx.message.channel, "Errors - can't find given roles...")
                return
            print("Found " + str(len(server_members)) + " members to analyze")
            for CurrentMember in server_members:
                if (action == "remove" or action == "-") and (selected_role in CurrentMember.roles):  # remove the role
                    await self.bot.remove_roles(CurrentMember, selected_role)
                    print("Role removed for user:" + CurrentMember.name)
                if (action == "add" or action == "+") and (selected_role not in CurrentMember.roles):  # add the role
                    await self.bot.add_roles(CurrentMember, selected_role)
                    print("Role added for user:" + CurrentMember.name)
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def editrole(self, ctx, *args):
        """Function that edit a user role (in the server where it's called)
        Usage: !editrole remove "ScrappyCocco" "NoobRole"
        Usage: !editrole add "ScrappyCocco" "ProRole"
        """
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't edit roles in private, execute the command in a server*")
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 3:
                await self.bot.send_message(ctx.message.channel, "Parameters not correct...")
                return
            print("-------------------------")
            action = str(args[0])
            if len(ctx.message.mentions) == 1:
                print("I've gon one mention")
                user_found = discord.utils.get(ctx.message.server.members, name=str(ctx.message.mentions[0].name))
            else:
                user_found = discord.utils.get(ctx.message.server.members, name=str(args[1]))
            role_to_update = discord.utils.get(ctx.message.server.roles, name=str(args[2]))
            if role_to_update is None or user_found is None:  # error searching the user
                await self.bot.send_message(ctx.message.channel, "Errors - can't find given roles...")
            else:
                if action == "add" or action == "+":
                    await self.bot.add_roles(user_found, role_to_update)
                if action == "remove" or action == "-":
                    await self.bot.remove_roles(user_found, role_to_update)
                print("Role Updated for user:" + user_found.name)
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # -------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def promoteusers(self, ctx, *args):
        """Function that change the role of ALL users from Old to New (in the server where it's called)
        Usage: !promoteusers "NoobRole" "ProRole"
        Usage: !promoteusers "EMPTY" "ProRole"
        """
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't edit roles in private, execute the command in a server*")
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 2:
                await self.bot.send_message(ctx.message.channel, "Parameters not correct...")
                return
            print("-------------------------")
            server_members = ctx.message.server.members
            empty_role = False
            old_role = None
            if str(args[0]).lower() == "empty":  # promote users without a role
                empty_role = True
            else:
                old_role = discord.utils.get(ctx.message.server.roles, name=str(args[0]))
            new_role = discord.utils.get(ctx.message.server.roles, name=str(args[1]))
            if (old_role is None or new_role is None) and not empty_role:
                await self.bot.send_message(ctx.message.channel, "Errors - can't find given roles...")
                return
            print("Found " + str(len(server_members)) + " members to analyze")
            for CurrentMember in server_members:
                if len(CurrentMember.roles) == 0 and empty_role:
                    await self.bot.add_roles(CurrentMember, new_role)
                else:
                    if old_role in CurrentMember.roles:
                        await self.bot.remove_roles(CurrentMember, old_role)
                        await self.bot.add_roles(CurrentMember, new_role)
                        print("Role Updated for user:" + CurrentMember.name)
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotModerationCommands(bot))
