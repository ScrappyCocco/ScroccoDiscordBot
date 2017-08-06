# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import discord
import requests
import time

from discord import channel
from datetime import datetime
from botVariablesClass import BotVariables
from botMethodsClass import BotMethods

# ---------------------------------------------------------------------


class BotMaintenanceCommands:
    """ Class with Bot 'Maintenance' commands (for example turning off the bot or changing user roles) """
    # ---------------------------------------------------------------------

    botVariables = BotVariables(False)  # used for version and In-Game state-write url

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
        """Set the bot in maintenance Mode (1=enabled 2=disabled)
        Usage: !maintenance 1
        """
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
            else:
                await self.bot.say("Parameters not correct")
            print("-------------------------")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def changestate(self, ctx, *args):
        """Change bot state
        Usage: !changestate 1
        """
        if BotMethods.is_owner(ctx.message.author):
            print("-------------------------")
            print("Changing bot state")
            new_status = discord.Status
            if len(args) == 1:  # switch between all states
                status_received = int(args[0])
                if status_received == 0:
                    new_status = discord.Status.online
                    print("State 0 - Online")
                if status_received == 1:
                    new_status = discord.Status.idle
                    print("State 1 - Idle")
                if status_received == 2:
                    new_status = discord.Status.do_not_disturb
                    print("State 2 - Dnd")
                if status_received == 3:
                    new_status = discord.Status.invisible
                    print("State 3 - Invisible")
                if status_received < 0 or status_received > 3:
                    print("State Not Correct, going online")
                    new_status = discord.Status.online
                # apply the state with the old in-game status
                await self.bot.change_presence(status=new_status, game=discord.Game(name=self.bot.lastInGameStatus))
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
                server_name = str(ctx.message.server.name)
                print("Region Found: " + region)
                await self.bot.say("Server Location: **" + server_name + "**: " + region)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def ver(self):
        """Print bot current version"""
        await self.bot.say("**Current Version:** " + self.botVariables.get_version()+" **Build:** "+self.botVariables.get_build())

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def channelid(self, ctx, *args):
        """Search a channel with the given name(in bot servers), if it exist, then it print the channel if
        Usage: !channelid public
        Usage: !channelid * (big command, take long time)
        """
        found = False
        if not BotMethods.is_owner(ctx.message.author):
            return
        if not len(args) == 1:  # params not correct
            return
        for currentServer in self.bot.servers:
            for current_channel in currentServer.channels:
                if current_channel.type == discord.ChannelType.text:  # if it's a text channel and not a voice channel
                    if current_channel.name == str(args[0]) or str(args[0]) == "*":  # the name is equal
                        found = True
                        await self.bot.send_message(ctx.message.channel, "**Channel Found:** " + current_channel.name + " - " + current_channel.server.name + " --> ID= " + current_channel.id)
        if not found:
            await self.bot.send_message(ctx.message.channel, "Nothing found...")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def servers(self, ctx):
        """Show all the servers where the bot is present
        Usage: !servers
        """
        found = False
        final_string = ""
        if not BotMethods.is_owner(ctx.message.author):
            return
        for currentServer in self.bot.servers:
            found = True
            final_string += currentServer.name + " - ID: " + str(currentServer.id) + " - " + str(currentServer.member_count) + " Members \n"
        if not found:
            await self.bot.send_message(ctx.message.channel, "Nothing found...")
        else:
            await self.bot.send_message(ctx.message.channel, final_string)

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def serverinfo(self, ctx):
        """Show the current server's info
        Usage: !serverinfo
        """
        if ctx.message.server is None:
            return
        server_selected = ctx.message.server
        embed = discord.Embed(title=server_selected.name,
                              colour=discord.Colour(0x169DDF),
                              description=server_selected.name+" server info",
                              timestamp=datetime.utcfromtimestamp(time.time())
                              )
        embed.set_thumbnail(url=server_selected.icon_url)
        embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
        embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())

        voice_channels_count = 0
        text_channels_count = 0
        for current_channel in server_selected.channels:
            if current_channel.type == channel.ChannelType.text:
                text_channels_count += 1
            if current_channel.type == channel.ChannelType.voice:
                voice_channels_count += 1

        embed.add_field(name="Server Region:", value=str(server_selected.region))
        embed.add_field(name="Server Owner:", value=str(server_selected.owner.name))
        embed.add_field(name="Server Members:", value=str(server_selected.member_count))
        embed.add_field(name="Server Creation:", value=str(server_selected.created_at))
        embed.add_field(name="Server Text Channels:", value=str(text_channels_count))
        embed.add_field(name="Server Voice Channels:", value=str(voice_channels_count))

        await self.bot.say(embed=embed)  # send the discord embed message with the servers info

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
                new_state = str(args[0])
                self.bot.lastInGameStatus = new_state  # update last state
                print("Changing my status in:" + new_state)
                url = self.botVariables.get_server_write_status_url()
                # request to save the state on the web
                if self.botVariables.emptyUrl not in url:
                    r = requests.post(url,
                                      data={self.botVariables.get_server_write_status_parameter(): new_state,
                                            })
                    if r.text == "Error" or not (r.status_code == 200):
                        print("ERROR SAVING NEW STATUS ON THE SERVER...")
                    else:
                        print("Status correctly saved on server...")
                else:
                    print("URL ERROR - ERROR SAVING NEW STATUS ON THE SERVER... Check bot data json")
                # change the bot in-game status
                await self.bot.change_presence(game=discord.Game(name=new_state))
                await self.bot.say("Status correctly changed and saved on server!")
        else:
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def sendservermessage(self, ctx, *args):
        """Send a message in a server channel
        Usage: !sendservermessage "ServerChannelId" "Message"
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

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def sendprivatemessage(self, ctx, *args):
        """Send a message in private (IF POSSIBLE)
        Usage: !sendprivatemessage "UserId" "Message"
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
    async def rename(self, ctx, *args):
        """Function that change the username of the bot
            Usage: !rename "NoobBot"
        """
        if not BotMethods.is_owner(ctx.message.author):
            await self.bot.say("You don't have access to this command  :stuck_out_tongue: ")
            return
        if len(args) == 1:
            print("-------------------------")
            new_name = args[0]
            print("BOT RENAME:"+new_name)
            await self.bot.edit_profile(username=new_name)
            print("-------------------------")
        else:
            await self.bot.say("Parameters not correct...")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->"+self.__class__.__name__+" class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotMaintenanceCommands(bot))
