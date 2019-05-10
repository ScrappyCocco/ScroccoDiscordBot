# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import discord

from botMethodsClass import BotMethods


# ---------------------------------------------------------------------


class BotModerationCommands(commands.Cog):
    """ Class with Bot 'Moderation' commands (for example ban and kick users) """

    # ---------------------------------------------------------------------

    async def checkcommandinserver(self, message: discord.message):
        if message.guild is None:
            await message.channel.send("*Can't execute this in private, execute the command in a server*")
            return True
        return False

    # ---------------------------------------------------------------------

    @commands.command()
    async def banuser(self, ctx: discord.ext.commands.Context):
        """Function that ban a user from the server
        Usage: !banuser @User
        """
        # Check that the command is not executed in private message
        message_channel: discord.abc.Messageable = ctx.message.channel
        if self.checkcommandinserver(ctx.message):
            return
        # Check that is a server admin that want to ban users (could check specifically for ban permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await message_channel.send("Error with mentions...")
                return
            print("-------------------------")
            # Try to ban the mentioned user
            try:
                async with message_channel.typing():
                    await ctx.message.guild.ban(ctx.message.mentions[0], delete_message_days=7)
                    await message_channel.send(str(ctx.message.mentions[0].name) + " has been banned")
            except discord.errors.Forbidden:
                await message_channel.send("Sorry, I don't have the `ban` permission")
            print("-------------------------")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command()
    async def unbanuser(self, ctx: discord.ext.commands.Context, *args):
        """Function that un-ban a user from the server
        Usage: !unbanuser UserID
        """
        # Check that the command is not executed in private message
        message_channel: discord.abc.Messageable = ctx.message.channel
        if self.checkcommandinserver(ctx.message):
            return
        # Check that is a server admin that want to ban users (could check specifically for unbanuser permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 1 or not str(args[0]).isdigit():
                await message_channel.send("Error with UserID...")
                return
            print("-------------------------")
            # Try to un-ban the mentioned user
            try:
                async with message_channel.typing():
                    await ctx.message.guild.unban(self.bot.get_user(int(args[0])))
                    await message_channel.send("A user has been un-banned!")
            except discord.errors.Forbidden:
                await message_channel.send("Sorry, I don't have the `unban` permission")
            print("-------------------------")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command()
    async def softban(self, ctx: discord.ext.commands.Context):
        """Function that soft-ban (=ban and unban deleting the messages) a user from the server
        Usage: !softban @User
        """
        # Check that the command is not executed in private message
        message_channel: discord.abc.Messageable = ctx.message.channel
        if self.checkcommandinserver(ctx.message):
            return
        # Check that is a server admin that want to ban users (could check specifically for banuser permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await message_channel.send("Error with mentions...")
                return
            print("-------------------------")
            # Ban and unban the current user
            try:
                async with message_channel.typing():
                    await ctx.message.guild.ban(ctx.message.mentions[0], delete_message_days=7)
                    await ctx.message.guild.unban(self.bot.get_user(int(ctx.message.mentions[0].id)))
                    await message_channel.send(str(ctx.message.mentions[0].name) + " has been soft-banned ")
            except discord.errors.Forbidden:
                await message_channel.send("Sorry, I don't have the `softban` permission")
            print("-------------------------")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command()
    async def kickuser(self, ctx: discord.ext.commands.Context):
        """Function that kick a user from the server
        Usage: !kickuser @User
        """
        # Check that the command is not executed in private message
        message_channel: discord.abc.Messageable = ctx.message.channel
        if self.checkcommandinserver(ctx.message):
            return
        # Check that is a server admin that want to ban users (could check specifically for kickuser permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(ctx.message.mentions) != 1:
                await message_channel.send("Error with mentions...")
                return
            print("-------------------------")
            # Kick the mentioned user
            try:
                async with message_channel.typing():
                    await ctx.message.guild.kick(ctx.message.mentions[0])
                    await message_channel.send(str(ctx.message.mentions[0].name) + " has been kicked")
            except discord.errors.Forbidden:
                await message_channel.send("Sorry, I don't have the `kick` permission")
            print("-------------------------")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command()
    async def kickbyrole(self, ctx: discord.ext.commands.Context, *args):
        """Function that kick all the users with a role from the server (USE WITH CAUTION!)
        Usage: !kickuser "NoobRole"
        """
        # Check that the command is not executed in private message
        message_channel: discord.abc.Messageable = ctx.message.channel
        if self.checkcommandinserver(ctx.message):
            return
        # Check that is a server admin that want to ban users (could check specifically for kickuser permission)
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 1:
                await message_channel.send("Parameters not correct...")
                return
            # Get all the members and the role
            server_members = ctx.message.guild.members
            selected_role = discord.utils.get(ctx.message.guild.roles, name=str(args[0]))
            # Check that the role exist
            if selected_role is None:
                await message_channel.send("Errors - can't find given role(no role called \"" + str(
                    args[0]) + "\" found)...")
                return
            print("Found " + str(len(server_members)) + " members to analyze")
            counter = 0
            # Try to kick all the users with that role
            try:
                async with message_channel.typing():
                    for current_member in server_members:
                        # Kick the user if he has that role
                        if selected_role in current_member.roles:
                            print("Found user to kick:" + current_member.name)
                            await ctx.message.guild.kick(current_member)
                            counter += 1
                    await message_channel.send("Successfully kicked " + str(counter) + " users with the given role!")
            except discord.errors.Forbidden:
                await message_channel.send("Sorry, I don't have the `kick` permission")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def editallroles(self, ctx: discord.ext.commands.Context, *args):
        """Function that change the role of ALL users (add/remove a role)
        USE WITH CAUTION
        Usage: !editallroles remove "NoobRole"
        Usage: !editallroles add "ProRole"
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if self.checkcommandinserver(ctx.message):
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 2 or (str(args[0]).lower() != "remove" and str(args[0]).lower() != "add"):
                await message_channel.send("Parameters not correct...")
                return
            print("-------------------------")
            server_members = ctx.message.guild.members
            action = str(args[0]).lower()
            selected_role = discord.utils.get(ctx.message.guild.roles, name=str(args[1]))
            if selected_role is None:
                await message_channel.send("Errors - can't find given roles...")
                return
            print("Found " + str(len(server_members)) + " members to analyze")
            counter = 0
            async with message_channel.typing():
                for current_member in server_members:
                    if (action == "remove") and (selected_role in current_member.roles):  # remove the role
                        await current_member.remove_roles(selected_role)
                        print("Role removed for user:" + current_member.name)
                        counter += 1
                    if (action == "add") and (selected_role not in current_member.roles):  # add the role
                        await current_member.add_roles(selected_role)
                        print("Role added for user:" + current_member.name)
                        counter += 1
                await message_channel.send(
                    "Successfully executed '" + action + " role' for " + str(counter) + " users!")
            print("-------------------------")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def editrole(self, ctx: discord.ext.commands.Context, *args):
        """Function that edit a user role (in the server where it's called)
        Usage: !editrole remove "ScrappyCocco" "NoobRole"
        Usage: !editrole add "ScrappyCocco" "ProRole"
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if self.checkcommandinserver(ctx.message):
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 3:
                await message_channel.send("Parameters not correct...")
                return
            print("-------------------------")
            action = str(args[0])
            # Get the user
            if len(ctx.message.mentions) == 1:
                print("I've gon one mention")
                user_found = discord.utils.get(ctx.message.guild.members, name=str(ctx.message.mentions[0].name))
            else:
                user_found = discord.utils.get(ctx.message.guild.members, name=str(args[1]))
            # Get the role with the name
            role_to_update = discord.utils.get(ctx.message.guild.roles, name=str(args[2]))
            if role_to_update is None or user_found is None:  # error searching the user
                await message_channel.send("Errors - can't find given roles...")
            else:
                # Add or remove the role
                if action == "add" or action == "+":
                    await user_found.add_roles(role_to_update)
                if action == "remove" or action == "-":
                    await user_found.remove_roles(role_to_update)
                await message_channel.send("Role Updated for user:" + user_found.name)
                print("Role Updated for user:" + user_found.name)
            print("-------------------------")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # -------------------------------------------------------------------

    @commands.command(hidden=True)
    async def promoteusers(self, ctx: discord.ext.commands.Context, *args):
        """Function that change the role of ALL users from Old to New (in the server where it's called)
        Usage: !promoteusers "NoobRole" "ProRole"
        Usage: !promoteusers "EMPTY" "ProRole"
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if self.checkcommandinserver(ctx.message):
            return
        if BotMethods.is_server_admin(ctx.message.author):
            if len(args) != 2:
                await message_channel.send("Parameters not correct...")
                return
            print("-------------------------")
            server_members = ctx.message.guild.members
            empty_role = False
            old_role = None
            if str(args[0]).lower() == "empty":  # promote users without a role
                empty_role = True
            else:
                old_role = discord.utils.get(ctx.message.guild.roles, name=str(args[0]))
            new_role = discord.utils.get(ctx.message.guild.roles, name=str(args[1]))
            if (old_role is None or new_role is None) and not empty_role:
                await message_channel.send("Errors - can't find given roles...")
                return
            print("Found " + str(len(server_members)) + " members to analyze")
            counter = 0
            # For every user check and add the role
            async with message_channel.typing():
                for current_member in server_members:
                    if len(current_member.roles) == 0 and empty_role:
                        await current_member.add_roles(new_role)
                        counter += 1
                    else:
                        if old_role in current_member.roles:
                            await current_member.remove_roles(old_role)
                            await current_member.add_roles(new_role)
                            print("Role Updated for user:" + current_member.name)
                            counter += 1
                await message_channel.send("Successfully updated role for " + str(counter) + " users!")
            print("-------------------------")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotModerationCommands(bot))
