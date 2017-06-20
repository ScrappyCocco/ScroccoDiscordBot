# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import discord
import requests

from botVariablesClass import BotVariables
from botMethodsClass import BotMethods

# ---------------------------------------------------------------------


class BotMaintenanceCommands:
    """ Class with Bot 'Maintenance' commands (for example turning off the bot or changing user roles) """
    # ---------------------------------------------------------------------

    botVariables = BotVariables()  # used for version and In-Game state-write url

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def off(self, ctx):
        """Turn off the bot"""
        print("---------------------------------------------------------------------------")
        print("Shut Down Required")
        if BotMethods.is_owner(ctx.message.author):
            await self.bot.say("Stopping bot... Bye!")
            await self.bot.logout()
            await self.bot.close()
        else:
            await self.bot.say("You don't have access to this command :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def maintenance(self, ctx, *args):
        """Set the bot in maintenance Mode (1=enabled 2=disabled)"""
        if BotMethods.is_owner(ctx.message.author):
            print("-------------------------")
            if len(args) == 1:
                if str(args[0]) == "1" or str(args[0]).lower() == "on":
                    print("Turning on maintenance mode")
                    await self.bot.change_presence(status=discord.Status.do_not_disturb,
                                                   game=discord.Game(name='IN MAINTENANCE'))
                    self.bot.maintenanceMode = True
                else:
                    print("Turning off maintenance mode")
                    await self.bot.change_presence(status=discord.Status.online,
                                                   game=discord.Game(name=self.bot.lastInGameStatus))
                    self.bot.maintenanceMode = False
            print("-------------------------")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def changestate(self, ctx, *args):
        """Change bot state"""
        if BotMethods.is_owner(ctx.message.author):
            print("-------------------------")
            print("Changing bot state")
            newStatus = discord.Status
            if len(args) == 1:  # switch between all states
                stateReceived = int(args[0])
                if stateReceived == 0:
                    newStatus = discord.Status.online
                    print("State 0 - Online")
                if stateReceived == 1:
                    newStatus = discord.Status.idle
                    print("State 1 - Idle")
                if stateReceived == 2:
                    newStatus = discord.Status.do_not_disturb
                    print("State 2 - Dnd")
                if stateReceived == 3:
                    newStatus = discord.Status.invisible
                    print("State 3 - Invisible")
                if stateReceived < 0 or stateReceived > 3:
                    print("State Not Correct, going online")
                    newStatus = discord.Status.online
                # apply the state with the old in-game status
                await self.bot.change_presence(status=newStatus, game=discord.Game(name=self.bot.lastInGameStatus))
            print("-------------------------")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def region(self, ctx):
        """Print server region"""
        print("-------------------------")
        if ctx is not None:
            if ctx.message.server is None:  # private message
                print("Can't find region in private chat")
            else:
                region = str(ctx.message.server.region)
                serverName = str(ctx.message.server.name)
                print("Region Found: " + region)
                await self.bot.say("Server Location: **" + serverName + "**: " + region)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def ver(self):
        """Print bot current version"""
        await self.bot.say("**Current Version:** " + self.botVariables.get_version())

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def channelid(self, ctx, *args):
        """Search a channel with the given name(in bot servers), if it exist, then it print the channel if"""
        found = False
        if not BotMethods.is_owner(ctx.message.author):
            return
        if not len(args) == 1:  # params not correct
            return
        for currentServer in self.bot.servers:
            for channel in currentServer.channels:
                if channel.type == discord.ChannelType.text:  # if it's a text channel and not a voice channel
                    if channel.name == str(args[0]):  # the name is equal
                        found = True
                        await self.bot.send_message(ctx.message.channel, "**Channel Found:** " + channel.name + " - " + channel.server.name + " --> ID= " + channel.id)
        if not found:
            await self.bot.send_message(ctx.message.channel, "Nothing found...")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def game(self, ctx, *args):
        """Edit bot In-Game string
        Usage: !game "new status"
        """
        print("-------------------------")
        if BotMethods.is_owner(ctx.message.author):
            if len(args) == 0 or len(args) > 1:
                await self.bot.say("I need only a parameter!")
            else:
                newState = str(args[0])
                self.bot.lastInGameStatus = newState  # update last state
                print("Changing my status in:" + newState)
                url = self.botVariables.writeStateUrl
                # request to save the state on the web
                r = requests.post(url,
                                  data={self.botVariables.writeStateParamName: newState,
                                        })
                if r.text == "Error":
                    print("ERROR SAVING NEW STATUS ON THE SERVER...")
                else:
                    print("Status correctly saved on server...")
                # change the bot in-game status
                await self.bot.change_presence(game=discord.Game(name=newState))
                await self.bot.say("Status correctly changed and saved on server!")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def sendservermessage(self, ctx, *args):
        """Send a message in a server channel
        Usage: !sendservermessage <ServerChannelId> "Message"
        """
        if BotMethods.is_owner(ctx.message.author):
            if len(args) == 2:
                channel_id = args[0]
                message = args[1]
                try:
                    await self.bot.send_message(discord.Server(id=int(channel_id)), message)
                except discord.errors.Forbidden:
                    print("ERROR: Can't send the message")
            else:
                await self.bot.say("Parameters not correct")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")

    @commands.command(pass_context=True, hidden=True)
    async def sendprivatemessage(self, ctx, *args):
        """Send a message in private
        Usage: !sendprivatemessage <UserId> "Message"
        """
        if BotMethods.is_owner(ctx.message.author):
            if len(args) == 2:
                recipient = args[0]
                message = args[1]
                try:
                    await self.bot.send_message(discord.User(id=int(recipient)), "**Message from " + ctx.message.author.name + ":**" + message)
                except discord.errors.Forbidden:
                    print("ERROR: Can't send the message")
            else:
                await self.bot.say("Parameters not correct")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def promoteusers(self, ctx, *args):
        """Function that change the role of ALL users from Old to New (in the server where it's called)
        Usage: !promoteusers "NoobRole" "ProRole"
        """
        if BotMethods.is_owner(ctx.message.author) or BotMethods.is_server_admin(ctx.message.author):
            if not len(args) == 2:
                await self.bot.say("Parameters not correct...")
                return
            print("-------------------------")
            if ctx.message.server is None:
                return
            serverMembers = ctx.message.server.members
            oldRole = discord.utils.get(ctx.message.server.roles, name=str(args[0]))
            newRole = discord.utils.get(ctx.message.server.roles, name=str(args[1]))
            if oldRole is None or newRole is None:
                await self.bot.say("Errors - can't find given roles...")
                return
            print("Found " + str(len(serverMembers)) + " members to analyze")
            for CurrentMember in serverMembers:
                if oldRole in CurrentMember.roles:
                        await self.bot.remove_roles(CurrentMember, oldRole)
                        await self.bot.add_roles(CurrentMember, newRole)
                        print("Role Updated for user:" + CurrentMember.name)
            print("-------------------------")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def editallroles(self, ctx, *args):
        """Function that change the role of ALL users (add/remove a role)
        Usage: !editallroles remove "NoobRole"
        Usage: !editallroles add "ProRole"
        """
        if BotMethods.is_owner(ctx.message.author) or BotMethods.is_server_admin(ctx.message.author):
            if not len(args) == 2:
                await self.bot.say("Parameters not correct...")
                return
            print("-------------------------")
            if ctx.message.server is None:
                return
            serverMembers = ctx.message.server.members
            action = str(args[0])
            selectedRole = discord.utils.get(ctx.message.server.roles, name=str(args[1]))
            if selectedRole is None:
                await self.bot.say("Errors - can't find given roles...")
                return
            print("Found " + str(len(serverMembers)) + " members to analyze")
            for CurrentMember in serverMembers:
                if selectedRole in CurrentMember.roles:
                    if action == "remove" or action == "-":  # remove the role
                        await self.bot.remove_roles(CurrentMember, selectedRole)
                        print("Role removed for user:" + CurrentMember.name)
                    if action == "add" or action == "+":  # add the role
                        await self.bot.add_roles(CurrentMember, selectedRole)
                        print("Role added for user:" + CurrentMember.name)
            print("-------------------------")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def editrole(self, ctx, *args):
        """Function that edit a user role (in the server where it's called)
        [DON'T work with mentions for now]
        Usage: !editrole remove "ScrappyCocco" "NoobRole"
        Usage: !editrole add "ScrappyCocco" "ProRole"
        """
        if BotMethods.is_owner(ctx.message.author) or BotMethods.is_server_admin(ctx.message.author):
            if not len(args) == 3:
                await self.bot.say("Parameters not correct...")
                return
            print("-------------------------")
            if ctx.message.server is None:  # it's a private message
                return
            action = str(args[0])
            userFound = discord.utils.get(ctx.message.server.members, name=str(args[1]))
            roleToSet = discord.utils.get(ctx.message.server.roles, name=str(args[2]))
            if roleToSet is None or userFound is None:  # error searching the user
                await self.bot.say("Errors - can't find given roles...")
            else:
                if action == "add" or action == "+":
                    await self.bot.add_roles(userFound, roleToSet)
                if action == "remove" or action == "-":
                    await self.bot.remove_roles(userFound, roleToSet)
                print("Role Updated for user:" + userFound.name)
            print("-------------------------")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->"+self.__class__.__name__+" class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotMaintenanceCommands(bot))
