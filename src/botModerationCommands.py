# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import discord

from botMethodsClass import BotMethods


# ---------------------------------------------------------------------


class BotModerationCommands(commands.Cog):
    """ Class with Bot 'Moderation' commands (for example ban and kick users) """

    # ---------------------------------------------------------------------

    @commands.command()
    async def banuser(self, ctx):
        """Function that ban a user from the server
        Usage: !banuser @User
        """
        # Check that the command is not executed in private message
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        # Check that is a server admin that want to ban users (could check specifically for ban permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await self.bot.send_message(ctx.message.channel, "Error with mentions...")
                return
            print("-------------------------")
            # Try to ban the mentioned user
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

    @commands.command()
    async def unbanuser(self, ctx, *args):
        """Function that un-ban a user from the server
        Usage: !unbanuser UserID
        """
        # Check that the command is not executed in private message
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        # Check that is a server admin that want to ban users (could check specifically for unbanuser permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 1 or not str(args[0]).isdigit():
                await self.bot.send_message(ctx.message.channel, "Error with UserID...")
                return
            print("-------------------------")
            # Try to un-ban the mentioned user
            try:
                await self.bot.unban(ctx.message.server, discord.Object(id=args[0]))
                await self.bot.send_message(ctx.message.channel, "A user has been un-banned!")
            except discord.errors.Forbidden:
                await self.bot.send_message(ctx.message.channel, "Sorry, I don't have the `unban` permission")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command()
    async def softban(self, ctx):
        """Function that soft-ban (=ban and unban deleting the messages) a user from the server
        Usage: !softban @User
        """
        # Check that the command is not executed in private message
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        # Check that is a server admin that want to ban users (could check specifically for banuser permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await self.bot.send_message(ctx.message.channel, "Error with mentions...")
                return
            print("-------------------------")
            # Ban and unban the current user
            try:
                await self.bot.ban(ctx.message.mentions[0], delete_message_days=100)
                await self.bot.unban(ctx.message.server, discord.Object(id=ctx.message.mentions[0].id))
                await self.bot.send_message(ctx.message.channel,
                                            str(ctx.message.mentions[0].name) + " has been soft-banned ")
            except discord.errors.Forbidden:
                await self.bot.send_message(ctx.message.channel, "Sorry, I don't have the `softban` permission")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command()
    async def kickuser(self, ctx):
        """Function that kick a user from the server
        Usage: !kickuser @User
        """
        # Check that the command is not executed in private message
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        # Check that is a server admin that want to ban users (could check specifically for kickuser permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await self.bot.send_message(ctx.message.channel, "Error with mentions...")
                return
            print("-------------------------")
            # Kick the mentioned user
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

    @commands.command()
    async def kickbyrole(self, ctx, *args):
        """Function that kick all the users with a role from the server (USE WITH CAUTION!)
        Usage: !kickuser "NoobRole"
        """
        # Check that the command is not executed in private message
        if ctx.message.server is None:
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't execute this in private, execute the command in a server*")
            return
        # Check that is a server admin that want to ban users (could check specifically for kickuser permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 1:
                await self.bot.send_message(ctx.message.channel, "Parameters not correct...")
                return
            # Get all the members and the role
            server_members = ctx.message.server.members
            selected_role = discord.utils.get(ctx.message.server.roles, name=str(args[0]))
            # Check that the role exist
            if selected_role is None:
                await self.bot.send_message(ctx.message.channel,
                                            "Errors - can't find given role(no role called \"" + str(
                                                args[0]) + "\" found)...")
                return
            print("Found " + str(len(server_members)) + " members to analyze")
            counter = 0
            # Try to kick all the users with that role
            try:
                for current_member in server_members:
                    # Kick the user if he has that role
                    if selected_role in current_member.roles:
                        print("Found user to kick:" + current_member.name)
                        await self.bot.kick(current_member)
                        counter += 1
                await self.bot.send_message(ctx.message.channel,
                                            "Successfully kicked " + str(counter) + " users with the given role!")
            except discord.errors.Forbidden:
                await self.bot.send_message(ctx.message.channel, "Sorry, I don't have the `kick` permission")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
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
            if len(args) != 2 or (str(args[0]).lower() != "remove" and str(args[0]).lower() != "add"):
                await self.bot.send_message(ctx.message.channel, "Parameters not correct...")
                return
            print("-------------------------")
            server_members = ctx.message.server.members
            action = str(args[0]).lower()
            selected_role = discord.utils.get(ctx.message.server.roles, name=str(args[1]))
            if selected_role is None:
                await self.bot.send_message(ctx.message.channel, "Errors - can't find given roles...")
                return
            print("Found " + str(len(server_members)) + " members to analyze")
            counter = 0
            for current_member in server_members:
                if (action == "remove") and (selected_role in current_member.roles):  # remove the role
                    await self.bot.remove_roles(current_member, selected_role)
                    print("Role removed for user:" + current_member.name)
                    counter += 1
                if (action == "add") and (selected_role not in current_member.roles):  # add the role
                    await self.bot.add_roles(current_member, selected_role)
                    print("Role added for user:" + current_member.name)
                    counter += 1
            await self.bot.send_message(ctx.message.channel,
                                        "Successfully executed '" + action + " role' for " + str(counter) + " users!")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
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
            # Get the user
            if len(ctx.message.mentions) == 1:
                print("I've gon one mention")
                user_found = discord.utils.get(ctx.message.server.members, name=str(ctx.message.mentions[0].name))
            else:
                user_found = discord.utils.get(ctx.message.server.members, name=str(args[1]))
            # Get the role with the name
            role_to_update = discord.utils.get(ctx.message.server.roles, name=str(args[2]))
            if role_to_update is None or user_found is None:  # error searching the user
                await self.bot.send_message(ctx.message.channel, "Errors - can't find given roles...")
            else:
                # Add or remove the role
                if action == "add" or action == "+":
                    await self.bot.add_roles(user_found, role_to_update)
                if action == "remove" or action == "-":
                    await self.bot.remove_roles(user_found, role_to_update)
                await self.bot.send_message(ctx.message.channel, "Role Updated for user:" + user_found.name)
                print("Role Updated for user:" + user_found.name)
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # -------------------------------------------------------------------

    @commands.command(hidden=True)
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
            counter = 0
            # For every user check and add the role
            for current_member in server_members:
                if len(current_member.roles) == 0 and empty_role:
                    await self.bot.add_roles(current_member, new_role)
                    counter += 1
                else:
                    if old_role in current_member.roles:
                        await self.bot.remove_roles(current_member, old_role)
                        await self.bot.add_roles(current_member, new_role)
                        print("Role Updated for user:" + current_member.name)
                        counter += 1
            await self.bot.send_message(ctx.message.channel,
                                        "Successfully updated role for " + str(counter) + " users!")
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
