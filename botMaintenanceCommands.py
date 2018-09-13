# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import discord
import requests
import time
import aiohttp

from discord import channel
from datetime import datetime
from botTimedTasks import BotTimedTasks
from botMethodsClass import BotMethods


# ---------------------------------------------------------------------


class BotMaintenanceCommands:
    """ Class with Bot 'Maintenance' commands (for example turning off the bot or changing bot status) """
    # ---------------------------------------------------------------------

    # list of class essential variables, the None variables are assigned in the constructor because i need the bot reference
    botVariables = None  # used for version and In-Game state-write url
    command_prefix = None

    TaskManager = None  # reference to "botTimedTasks" to create/stop tasks
    Timed_Tasks = []

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def off(self, ctx):
        """Turn off the bot"""
        print("---------------------------------------------------------------------------")
        print("Shut Down Required")
        if BotMethods.is_owner(ctx.message.author):
            await self.bot.send_message(ctx.message.channel, "Stopping bot... Bye!")
            # stopping tasks
            for C_Task in self.Timed_Tasks:
                C_Task.cancel()
                print("UNLOADING-->Timed-Task cancelled")
            del self.TaskManager  # delete the task manager
            await self.bot.logout()
            # await self.bot.close() not necessary apparently
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def maintenance(self, ctx, *args):
        """Set the bot in maintenance Mode (1=enabled other=disabled)
        Usage: !maintenance 1
        """
        if BotMethods.is_owner(ctx.message.author):
            print("-------------------------")
            if len(args) == 1:
                if str(args[0]) == "1" or str(args[0]).lower() == "on":
                    print("Turning on maintenance mode")
                    await self.bot.change_presence(status=discord.Status.do_not_disturb,
                                                   game=discord.Game(name='UNDER MAINTENANCE'))
                    self.bot.maintenanceMode = True
                else:
                    print("Turning off maintenance mode")
                    await self.bot.change_presence(status=discord.Status.online,
                                                   game=discord.Game(name=self.bot.lastInGameStatus))
                    self.bot.maintenanceMode = False
            else:
                await self.bot.send_message(ctx.message.channel,
                                            "Parameters not correct, see " + self.command_prefix + "help maintenance")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def changestate(self, ctx, *args):
        """Change bot state
        Usage: !changestate 0/1/2/3
        Usage: !changestate 4 "Streaming Title" "Twitch Stream URL"
        """
        if BotMethods.is_owner(ctx.message.author):
            print("-------------------------")
            print("Changing bot state")
            new_status = discord.Status
            if len(args) == 1 or len(args) == 3:  # switch between all states
                status_received = int(args[0])
                self.bot.isInStreamingStatus = False
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
                if status_received == 4:
                    self.bot.isInStreamingStatus = True
                    await self.bot.change_presence(
                        game=discord.Game(name=str(args[1]), url=str(args[2]), type=1))
                    print("Streaming status applied")
                    return
                if status_received < 0 or status_received > 3:
                    print("State Not Correct, going online")
                    new_status = discord.Status.online
                # apply the state with the old in-game status
                await self.bot.change_presence(status=new_status, game=discord.Game(name=self.bot.lastInGameStatus))
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def region(self, ctx):
        """Print server region"""
        print("-------------------------")
        if ctx is not None:
            if ctx.message.server is None:  # private message
                print("Can't find region in private chat")
                await self.bot.send_message(ctx.message.channel, "*Can't get server-region in private*")
            else:
                region = str(ctx.message.server.region)
                server_name = str(ctx.message.server.name)
                print("Region Found: " + region)
                await self.bot.send_message(ctx.message.channel, "Server Location: **" + server_name + "**: " + region)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def joined(self, ctx):
        """Print the date when you joined the server
        Usage: !joined To get your join date
        or !joined @User To get User's join date
        """
        print("-------------------------")
        if ctx is not None:
            if ctx.message.server is None:  # private message
                print("Can't find join-date in private chat")
                await self.bot.send_message(ctx.message.channel, "*Can't get join-date in private channel*")
            else:
                date = ""
                mention = False
                if len(ctx.message.mentions) == 1:
                    mention = True
                    for CurrentMember in ctx.message.server.members:
                        if CurrentMember.id == ctx.message.mentions[0].id:
                            date = CurrentMember.joined_at
                            break
                else:
                    date = ctx.message.author.joined_at
                date_string = date.strftime('%H:%M:%S %d-%m-%Y')
                if mention:
                    await self.bot.send_message(ctx.message.channel,
                                                "**" + ctx.message.mentions[0].name + "** joined this server: " + str(
                                                    date_string))
                else:
                    await self.bot.send_message(ctx.message.channel,
                                                "**" + ctx.message.author.name + "** joined this server: " + str(
                                                    date_string))
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def source(self, ctx):
        """Print a link to bot source code"""
        await self.bot.send_message(ctx.message.channel,
                                    "Go and explore my source code at: " + self.botVariables.get_open_source_link())

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def commands_list(self, ctx):
        """Display all the commands of the bot (even the hidden commands)
            Usage: !commands_list
        """
        if ctx.message.server is None:  # private message
            await self.bot.send_message(ctx.message.channel,
                                        "*Can't check if you're an admin in private chat. Execute this command in a server*")
            return
        if BotMethods.is_owner(ctx.message.author) or BotMethods.is_server_admin(ctx.message.author):
            final_string = "```LIST OF ALL BOT COMMANDS, SEE " + self.command_prefix + "HELP COMMAND FOR OTHER INFORMATIONS \n \n"
            for cmd in self.bot.commands:
                final_string += str(cmd) + "\n"
            final_string += "```"
            await self.bot.send_message(ctx.message.author, final_string)
            if ctx.message.server is not None:  # not in private message
                await self.bot.send_message(ctx.message.channel, "*List sent in private*")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def ver(self, ctx):
        """Print bot current version"""
        await self.bot.send_message(ctx.message.channel, "**Current Bot Version:** " + self.botVariables.get_version()
                                    + " **Build:** " + self.botVariables.get_build()
                                    + " - **API Version:** " + discord.__version__)

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def channelid(self, ctx, *args):
        """Search a channel with the given name(in bot servers), if it exist, then it print the channel if
        Usage: !channelid public
        Usage: !channelid * (show all channels in all servers, big command, take long time)
        """
        found = False
        if not BotMethods.is_owner(ctx.message.author):
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command :stuck_out_tongue: ")
            return
        if len(args) != 1:  # params not correct
            await self.bot.send_message(ctx.message.channel,
                                        "Parameters not correct, see " + self.command_prefix + "help channelid")
            return
        final_string = ""
        for currentServer in self.bot.servers:
            for current_channel in currentServer.channels:
                if current_channel.type == discord.ChannelType.text:  # if it's a text channel and not a voice channel
                    if current_channel.name == str(args[0]) or str(args[0]) == "*":  # the name is equal
                        found = True
                        final_string += "**Channel Found:** " + current_channel.name + " - " + current_channel.server.name + " --> ID= " + current_channel.id + "\n"
        if not found:
            await self.bot.send_message(ctx.message.channel, "Nothing found...")
        else:
            await self.bot.send_message(ctx.message.channel, final_string)

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def servers(self, ctx):
        """Show all the servers where the bot is present
        Usage: !servers
        """
        found = False
        final_string = ""
        if not BotMethods.is_owner(ctx.message.author):
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command :stuck_out_tongue: ")
            return
        for currentServer in self.bot.servers:
            found = True
            final_string += currentServer.name + " - ID: " + str(currentServer.id) + " - " + str(
                currentServer.member_count) + " Members \n"
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
            await self.bot.send_message(ctx.message.channel, "*Can't get server-info in private*")
            return
        server_selected = ctx.message.server
        embed = discord.Embed(title=server_selected.name,
                              colour=discord.Colour(0x169DDF),
                              description=server_selected.name + " server info",
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
        embed.add_field(name="Server Creation:", value=str(server_selected.created_at.strftime('%H:%M:%S %d-%m-%Y')))
        embed.add_field(name="Server Text Channels:", value=str(text_channels_count))
        embed.add_field(name="Server Voice Channels:", value=str(voice_channels_count))

        await self.bot.send_message(ctx.message.channel,
                                    embed=embed)  # send the discord embed message with the servers info

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def discordstatus(self, ctx):
        """Print the current Discord Status
        Usage: !discordstatus
        """
        await self.bot.send_message(ctx.message.channel, "This command is not ready, sorry")
        return
        print("-------------------------")
        url = "https://srhpyqt94yxb.statuspage.io/api/v2/summary.json"
        async with aiohttp.ClientSession() as session:  # async GET request
            async with session.get(url) as resp:
                r_json = await resp.json()
        if str(r_json["status"]["indicator"]) != "none" or len(r_json["incidents"]) != 0:
            print("Discord Status seems Not Normal - There is a problem with Discord Servers")
            embed = discord.Embed(title="Discord Server Status", url=str(r_json["incidents"][0]["shortlink"]),
                                  color=0x7289DA)
            embed.set_author(name="Analysis required by " + ctx.message.author.name,
                             icon_url=ctx.message.author.avatar_url)
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/276674976210485248/304963039545786368/1492797249_shield-error.png')
            embed.add_field(name="Incidents:", value="Everything is ok! No problems found", inline=False)
            for i in range(min(3, len(r_json["incidents"][0])), 0, -1):
                print("Not ready")
                # TODO - NEED A DISCORD STATUS JSON TO END THIS COMMAND
        else:
            print("Discord Status seems Normal")
            embed = discord.Embed(title="Discord Server Status", url="https://status.discordapp.com/",
                                  color=0x7289DA)
            embed.set_author(name="Analysis required by " + ctx.message.author.name,
                             icon_url=ctx.message.author.avatar_url)
            embed.set_thumbnail(
                url='https://cdn.discordapp.com/attachments/276674976210485248/304961315326394369/1492796826_Tick_Mark_Dark.png')
            embed.add_field(name="Result:", value="Everything is ok! No problems found", inline=False)
        # embed footer
        datetime_object = datetime.strptime(str(r_json["page"]["updated_at"][0:19]), '%Y-%m-%dT%H:%M:%S')
        embed.set_footer(
            text="Discord Status updated at: " + str(datetime_object.strftime('%H:%M:%S %d-%m-%Y')) + " timezone: " +
                 r_json["page"]["time_zone"], icon_url=self.botVariables.get_bot_icon())
        # send the embed
        await self.bot.send_message(ctx.message.channel,
                                    embed=embed)  # send the discord embed message with the servers status info
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def game(self, ctx, *args):
        """Edit bot In-Game string
        Usage: !game "new single status"
        Usage: !game "{Hello 1---JS Suck!---I'm a bot}"
        """
        print("-------------------------")
        if BotMethods.is_owner(ctx.message.author):
            if len(args) == 0:
                await self.bot.send_message(ctx.message.channel, "Current status: " + str(self.bot.lastInGameStatus))
            else:
                if len(args) > 1:
                    await self.bot.send_message(ctx.message.channel, "I need only a parameter!")
                    return
                new_state = str(args[0])
                # Is a list of states
                if new_state.startswith("{") and new_state.endswith("}"):
                    # Save that is a list
                    self.bot.hasAListOfStates = True
                    # Save the list removing the {} and splitting the text
                    self.bot.listOfStates = BotMethods.create_list_from_states_string(new_state)
                    # Randomize and use the state
                    new_state_to_use = BotMethods.get_random_bot_state(self.bot.listOfStates)
                    self.bot.lastInGameStatus = new_state_to_use
                else:  # Is not a list of states, change the state normally
                    self.bot.hasAListOfStates = False
                    self.bot.lastInGameStatus = new_state  # update last state
                    new_state_to_use = new_state
                print("Changing my status in:" + new_state_to_use)
                url = self.botVariables.get_server_write_status_url()
                # request to save the state on the web
                if self.botVariables.emptyUrl not in url and self.botVariables.get_bot_save_state_to_server():
                    r = requests.post(url,
                                      data={self.botVariables.get_server_write_status_parameter(): new_state,
                                            })
                    print("Change State - HTTP Request Status Code:" + str(r.status_code))
                    if r.text == "Error" or (r.status_code != 200):
                        print("ERROR SAVING NEW STATUS ON THE SERVER...")
                    else:
                        print("Status correctly saved on server...")
                else:
                    if self.botVariables.get_bot_save_state_to_file():
                        file = open(self.botVariables.get_bot_save_state_file_name(), "w")
                        file.write(new_state)
                        file.close()
                        print("Status file successfully opened and overwritten")
                    else:
                        print("No save state on file or server found - ERROR SAVING NEW STATUS... Check bot data json")
                # change the bot in-game status
                if self.bot.isInStreamingStatus:
                    await self.bot.send_message(ctx.message.channel,
                                                "The bot is currently in streaming status, state saved but not changed")
                else:
                    await self.bot.change_presence(game=discord.Game(name=new_state_to_use))
                    await self.bot.send_message(ctx.message.channel, "Status correctly changed!")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")
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
                await self.bot.send_message(ctx.message.channel,
                                            "Parameters not correct, see " + self.command_prefix + "help sendservermessage")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

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
                    await self.bot.send_message(discord.User(id=int(recipient)),
                                                "**Message from " + ctx.message.author.name + ":**" + message)
                except discord.errors.Forbidden:
                    print("ERROR: Can't send the message")
            else:
                await self.bot.send_message(ctx.message.channel,
                                            "Parameters not correct, see " + self.command_prefix + "help sendprivatemessage")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def rename(self, ctx, *args):
        """Function that change the username of the bot
            Usage: !rename "NoobBot"
        """
        if not BotMethods.is_owner(ctx.message.author):
            await self.bot.send_message(ctx.message.channel,
                                        "You don't have access to this command  :stuck_out_tongue: ")
            return
        if len(args) == 1:
            print("-------------------------")
            new_name = args[0]
            print("BOT RENAME:" + new_name)
            await self.bot.edit_profile(username=new_name)
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel, "Parameters not correct...")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot
        self.botVariables = self.bot.bot_variables_reference
        # assigning variables value now i can use botVariables
        self.command_prefix = self.botVariables.command_prefix
        # create youtube and discord-status task
        self.TaskManager = BotTimedTasks(self.bot)
        self.Timed_Tasks.append(self.bot.loop.create_task(self.TaskManager.youtube_check()))
        self.Timed_Tasks.append(self.bot.loop.create_task(self.TaskManager.discord_status_check()))
        self.Timed_Tasks.append(self.bot.loop.create_task(self.TaskManager.randomize_bot_status()))

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotMaintenanceCommands(bot))
