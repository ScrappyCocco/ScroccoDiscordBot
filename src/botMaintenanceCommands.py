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


class BotMaintenanceCommands(commands.Cog):
    """ Class with Bot 'Maintenance' commands (for example turning off the bot or changing bot status) """
    # ---------------------------------------------------------------------

    # list of class essential variables, the None variables are assigned in the constructor because i need the bot reference
    botVariables = None  # used for version and In-Game state-write url
    command_prefix = None

    TaskManager = None  # reference to "botTimedTasks" to create/stop tasks
    Timed_Tasks = []

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def off(self, ctx: discord.ext.commands.Context):
        """Turn off the bot"""
        print("---------------------------------------------------------------------------")
        print("Shut Down Required")
        message_channel: discord.abc.Messageable = ctx.message.channel
        if BotMethods.is_owner(ctx.message.author):
            await message_channel.send("Stopping bot... Bye!")
            # stopping tasks
            for c_task in self.Timed_Tasks:
                c_task.cancel()
                print("UNLOADING-->Timed-Task cancelled")
            del self.TaskManager  # delete the task manager
            await self.bot.logout()
            # await self.bot.close() not necessary apparently
        else:
            await message_channel.send("You don't have access to this command :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def maintenance(self, ctx: discord.ext.commands.Context, *args):
        """Set the bot in maintenance Mode (1=enabled other=disabled)
        Usage: !maintenance 1
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if BotMethods.is_owner(ctx.message.author):
            print("-------------------------")
            if len(args) == 1:
                if str(args[0]) == "1" or str(args[0]).lower() == "on":
                    print("Turning on maintenance mode")
                    await self.bot.change_presence(status=discord.Status.do_not_disturb,
                                                   activity=discord.Game(name='UNDER MAINTENANCE'))
                    self.bot.maintenanceMode = True
                else:
                    print("Turning off maintenance mode")
                    await self.bot.change_presence(status=discord.Status.online,
                                                   activity=discord.Game(name=getattr(self.bot, 'lastInGameStatus')))
                    self.bot.maintenanceMode = False
            else:
                await message_channel.send("Parameters not correct, see " + self.command_prefix + "help maintenance")
            print("-------------------------")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def changestate(self, ctx: discord.ext.commands.Context, *args):
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
                        activity=discord.Game(name=str(args[1]), url=str(args[2]), type=1))
                    print("Streaming status applied")
                    return
                if status_received < 0 or status_received > 3:
                    print("State Not Correct, going online")
                    new_status = discord.Status.online
                # apply the state with the old in-game status
                await self.bot.change_presence(status=new_status, activity=discord.Game(name=getattr(self.bot, 'lastInGameStatus')))
            print("-------------------------")
        else:
            message_channel: discord.abc.Messageable = ctx.message.channel
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command()
    async def region(self, ctx: discord.ext.commands.Context):
        """Print server region"""
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        if ctx is not None:
            if ctx.message.guild is None:  # private message
                print("Can't find region in private chat")
                await message_channel.send("*Can't get server-region in private*")
            else:
                region = str(ctx.message.server.region)
                server_name = str(ctx.message.server.name)
                print("Region Found: " + region)
                await message_channel.send("Server Location: **" + server_name + "**: " + region)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def joined(self, ctx: discord.ext.commands.Context):
        """Print the date when you joined the server
        Usage: !joined To get your join date
        or !joined @User To get User's join date
        """
        if ctx is not None:
            message_channel: discord.abc.Messageable = ctx.message.channel
            if ctx.message.server is None:  # private message
                print("Can't find join-date in private chat")
                await message_channel.send("*Can't get join-date in private channel*")
            else:
                date = ""
                mention = False
                if len(ctx.message.mentions) == 1:
                    mention = True
                    for current_member in ctx.message.server.members:
                        if current_member.id == ctx.message.mentions[0].id:
                            date = current_member.joined_at
                            break
                else:
                    date = ctx.message.author.joined_at
                date_string = date.strftime('%H:%M:%S %d-%m-%Y')
                if mention:
                    await message_channel.send("**" + ctx.message.mentions[0].name + "** joined this server: " + str(
                                                    date_string))
                else:
                    await message_channel.send("**" + ctx.message.author.name + "** joined this server: " + str(
                                                    date_string))

    # ---------------------------------------------------------------------

    @commands.command()
    async def birthday(self, ctx: discord.ext.commands.Context):
        """Print the date when you created your discord account
        Usage: !birthday To get your account creation date
        or !birthday @User To get User's birthday
        """
        if ctx is not None:
            message_channel: discord.abc.Messageable = ctx.message.channel
            mention = False
            if ctx.message.server is None:  # private message
                date = ctx.message.author.created_at
            else:
                date = ""
                mention = False
                if len(ctx.message.mentions) == 1:
                    mention = True
                    for current_member in ctx.message.server.members:
                        if current_member.id == ctx.message.mentions[0].id:
                            date = current_member.created_at
                            break
                else:
                    date = ctx.message.author.joined_at
            date_string = date.strftime('%H:%M:%S %d-%m-%Y')
            if mention:
                await message_channel.send("**" + ctx.message.mentions[
                                                0].name + "** created his Discord account: " + str(
                                                date_string))
            else:
                await message_channel.send("**" + ctx.message.author.name + "** created his Discord account: " + str(
                                                date_string))

    # ---------------------------------------------------------------------

    @commands.command()
    async def source(self, ctx: discord.ext.commands.Context):
        """Print a link to bot source code"""
        message_channel: discord.abc.Messageable = ctx.message.channel
        await message_channel.send("Go and explore my source code at: " + self.botVariables.get_open_source_link())

    # ---------------------------------------------------------------------

    @commands.command()
    async def commands_list(self, ctx: discord.ext.commands.Context):
        """Display all the commands of the bot (even the hidden commands)
            Usage: !commands_list
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if ctx.message.guild is None:  # private message
            await message_channel.send("*Can't check if you're an admin in private chat. Execute this command in a server*")
            return
        if BotMethods.is_owner(ctx.message.author) or BotMethods.is_server_admin(ctx.message.author):
            final_string = "```LIST OF ALL BOT COMMANDS, SEE " + self.command_prefix + "HELP COMMAND FOR OTHER INFORMATIONS \n \n"
            for cmd in self.bot.commands:
                final_string += str(cmd) + "\n"
            final_string += "```"
            await ctx.message.author.dm_channel.send(final_string)
            if ctx.message.server is not None:  # not in private message
                await message_channel.send("*List sent in private*")
        else:
            await message_channel.send("You don't have access to this command :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command()
    async def ver(self, ctx: discord.ext.commands.Context):
        """Print bot current version"""
        message_channel: discord.abc.Messageable = ctx.message.channel
        await message_channel.send("**Current Bot Version:** " + self.botVariables.get_version()
                                    + " **Build:** " + self.botVariables.get_build()
                                    + " - **API Version:** " + discord.__version__)

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def channelid(self, ctx: discord.ext.commands.Context, *args):
        """Search a channel with the given name(in bot servers), if it exist, then it print the channel if
        Usage: !channelid public
        Usage: !channelid * (show all channels in all servers, big command, take long time)
        """
        found = False
        message_channel: discord.abc.Messageable = ctx.message.channel
        if not BotMethods.is_owner(ctx.message.author):
            await message_channel.send("You don't have access to this command :stuck_out_tongue: ")
            return
        if len(args) != 1:  # params not correct
            await message_channel.send("Parameters not correct, see " + self.command_prefix + "help channelid")
            return
        final_string = ""
        for current_server in self.bot.guilds:
            for current_channel in current_server.channels:
                if current_channel.type == discord.ChannelType.text:  # if it's a text channel and not a voice channel
                    if current_channel.name == str(args[0]) or str(args[0]) == "*":  # the name is equal
                        found = True
                        final_string += "**Channel Found:** " + current_channel.name + " - " + current_channel.server.name + " --> ID= " + current_channel.id + "\n"
        if not found:
            await message_channel.send("Nothing found...")
        else:
            await message_channel.send(final_string)

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def servers(self, ctx: discord.ext.commands.Context):
        """Show all the servers where the bot is present
        Usage: !servers
        """
        found = False
        final_string = ""
        message_channel: discord.abc.Messageable = ctx.message.channel
        if not BotMethods.is_owner(ctx.message.author):
            await message_channel.send("You don't have access to this command :stuck_out_tongue: ")
            return
        for current_server in self.bot.guilds:
            found = True
            final_string += current_server.name + " - ID: " + str(current_server.id) + " - " + str(
                current_server.member_count) + " Members \n"
        if not found:
            await message_channel.send("Nothing found...")
        else:
            await message_channel.send(final_string)

    # ---------------------------------------------------------------------

    @commands.command()
    async def serverinfo(self, ctx: discord.ext.commands.Context):
        """Show the current server's info
        Usage: !serverinfo
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if ctx.message.guild is None:
            await message_channel.send("*Can't get server-info in private*")
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

        await message_channel.send(embed=embed)  # send the discord embed message with the servers info

    # ---------------------------------------------------------------------

    @commands.command()
    async def discordstatus(self, ctx: discord.ext.commands.Context):
        """Print the current Discord Status
        Usage: !discordstatus
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
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
            embed.add_field(name="Incidents:", value=str(r_json["incidents"][0]["name"]), inline=False)
            # Go from min(3, len(r_json["incidents"][0]["incident_updates"])-1) (3 or len-1) to -1 to print 3 incident updates
            for i in range(min(3, len(r_json["incidents"][0]["incident_updates"]) - 1), -1, -1):
                update_date_object = datetime.strptime(
                    r_json["incidents"][0]["incident_updates"][i]["updated_at"][0:19], '%Y-%m-%dT%H:%M:%S')
                embed.add_field(name="Incident Update:" + str(
                    r_json["incidents"][0]["incident_updates"][i]["status"]) + " - Updated at:" + str(
                    update_date_object.strftime('%H:%M:%S %d-%m-%Y')),
                                value=str(r_json["incidents"][0]["incident_updates"][i]["body"]),
                                inline=False)
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
        await message_channel.send(embed=embed)  # send the discord embed message with the servers status info
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def game(self, ctx: discord.ext.commands.Context, *args):
        """Edit bot In-Game string
        Usage: !game "new single status"
        Usage: !game "{Hello 1---JS Suck!---I'm a bot}"
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        if BotMethods.is_owner(ctx.message.author):
            if len(args) == 0:
                # If the bot has a list of states i print all the possible states
                if self.bot.hasAListOfStates:
                    list_of_states = ""
                    # Create a string with all the states
                    for bot_state in self.bot.listOfStates:
                        list_of_states += bot_state + ", "
                    await message_channel.send("Current status: " + str(
                                                    self.bot.lastInGameStatus) + "\nFrom list of states:{" + list_of_states + "}")
                else:
                    await message_channel.send("Current status: " + str(self.bot.lastInGameStatus))
            else:
                if len(args) > 1:
                    await message_channel.send("I need only a parameter!")
                    return
                new_state = str(args[0])
                # Is a list of states
                if new_state.startswith("{") and new_state.endswith("}"):
                    print("List of states found, saving and randomizing status...")
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
                if getattr(self.bot, 'isInStreamingStatus'):
                    await message_channel.send("The bot is currently in streaming status, state saved but not changed")
                else:
                    await self.bot.change_presence(activity=discord.Game(name=new_state_to_use))
                    await message_channel.send("Status correctly changed!")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def sendservermessage(self, ctx: discord.ext.commands.Context, *args):
        """Send a message in a server channel
        Usage: !sendservermessage "ServerChannelId" "Message"
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if BotMethods.is_owner(ctx.message.author):
            if len(args) == 2:
                channel_id = args[0]
                message = args[1]
                try:
                    await self.bot.get_channel(int(channel_id)).send(message)
                except discord.errors.Forbidden:
                    print("ERROR: Can't send the message")
            else:
                await message_channel.send("Parameters not correct, see " + self.command_prefix + "help sendservermessage")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def sendprivatemessage(self, ctx: discord.ext.commands.Context, *args):
        """Send a message in private (IF POSSIBLE)
        Usage: !sendprivatemessage "UserId" "Message"
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if BotMethods.is_owner(ctx.message.author):
            if len(args) == 2:
                recipient = args[0]
                message = args[1]
                try:
                    await self.bot.get_user(int(recipient)).dm_channel.send("**Message from " + ctx.message.author.name + ":**" + message)
                except discord.errors.Forbidden:
                    print("ERROR: Can't send the message")
            else:
                await message_channel.send("Parameters not correct, see " + self.command_prefix + "help sendprivatemessage")
        else:
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def rename(self, ctx: discord.ext.commands.Context, *args):
        """Function that change the username of the bot
            Usage: !rename "NoobBot"
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if not BotMethods.is_owner(ctx.message.author):
            await message_channel.send("You don't have access to this command  :stuck_out_tongue: ")
            return
        if len(args) == 1:
            print("-------------------------")
            new_name = args[0]
            print("BOT RENAME:" + new_name)
            await self.bot.user.edit(username=new_name)
            print("-------------------------")
        else:
            await message_channel.send("Parameters not correct...")

    # ---------------------------------------------------------------------

    def __init__(self, bot: discord.ext.commands.Bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot: discord.ext.commands.Bot = bot
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
