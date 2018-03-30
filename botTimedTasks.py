# ---------------------------------------------------------------------
# IMPORTS

from botVariablesClass import BotVariables

import aiohttp
import discord
import asyncio
import datetime


# ---------------------------------------------------------------------


class BotTimedTasks:
    """ Class with Bot Timed Tasks (tasks with timer) """
    ''' This class is created by "botMaintenanceCommands", 
    this because that class need to close the tasks before stopping the bot to avoid warnings/errors '''
    # ---------------------------------------------------------------------

    botVariables = BotVariables(False)  # used for 2 api keys
    YT_key = botVariables.get_youtube_api_key()
    YT_watchLink = "https://www.youtube.com/watch?v="

    statusChanged = False  # to skip continuous status change

    # ---------------------------------------------------------------------
    # this task check every hour for a new video of the specified channel, sending a message if a new video is found

    async def youtube_check(self):
        await self.bot.wait_until_ready()  # wait until the bot is ready
        print("------------------------")
        current_time = datetime.datetime.now() - datetime.timedelta(
            hours=1)  # check new videos in the past hour (current time - 1h)
        current_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 time format
        print("YT First check:" + str(current_time))
        while not self.bot.is_closed:
            if not self.bot.maintenanceMode:  # check for maintenanceMode (if yes, let's skip task content for safety)
                # create url with parameters
                for channel in self.botVariables.get_list_youtube_channels_check():
                    url = "https://www.googleapis.com/youtube/v3/activities?channelId=" + channel['YTchannelID'] \
                          + "&key=" + self.YT_key + "&part=snippet,contentDetails&publishedAfter=" + str(current_time)
                    async with aiohttp.ClientSession() as session:  # async GET request
                        async with session.get(url) as resp:
                            r_json = await resp.json()
                    if "error" in r_json:  # an error occurred with the request
                        print("An error occurred in YT timed request")
                        print(str(r_json))
                    else:  # no errors
                        if int(r_json['pageInfo']['totalResults']) == 1:  # if there is a new video
                            print("New video found, sending message")
                            message = channel['notificationMessage'] + "\n**" + r_json['items'][0]['snippet'][
                                'title'] + "** \n" + self.YT_watchLink + r_json['items'][0]['contentDetails']['upload'][
                                          'videoId'] + "\n"
                            try:
                                await self.bot.send_message(discord.Server(id=int(channel['DISCORDchannelID'])), message)
                            except discord.errors.Forbidden:
                                print("ERROR: Can't send the message in the specified channel")
                            print("Youtube Notification Message sent!")
                # end for each channel
                print("End of Youtube check for " + str(len(self.botVariables.get_list_youtube_channels_check())) + " channel(s)")
            await asyncio.sleep(3600)  # task runs every hour
            print("------------------------")
            current_time = datetime.datetime.now() - datetime.timedelta(
                hours=1)  # check new videos in the past hour (current time - 1h)
            current_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 time format
            print("YT check:" + str(current_time))
        print("--Youtube Task loop finished--")

    # ---------------------------------------------------------------------
    # this task check every hour for a new video of the specified channel, sending a message if a new video is found

    async def discord_status_check(self):
        await self.bot.wait_until_ready()  # wait until the bot is ready
        print("------------------------")
        current_time = datetime.datetime.now() - datetime.timedelta(
            hours=1)  # check new videos in the past hour (current time - 1h)
        current_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 time format
        print("Discord Status First check:" + str(current_time))
        while not self.bot.is_closed:
            if not self.bot.maintenanceMode:  # check for maintenanceMode (if yes, let's skip task content for safety)
                url = "https://srhpyqt94yxb.statuspage.io/api/v2/summary.json"
                async with aiohttp.ClientSession() as session:  # async GET request
                    async with session.get(url) as resp:
                        r_json = await resp.json()
                if str(r_json["status"]["indicator"]) != "none" or len(r_json["incidents"]) != 0:
                    if not self.statusChanged:
                        await self.bot.change_presence(status=discord.Status.do_not_disturb, game=discord.Game(
                            name="Discord Error - Check status.discordapp.com"))
                        self.statusChanged = True
                else:
                    if self.statusChanged:
                        self.statusChanged = False
                        await self.bot.change_presence(status=discord.Status.online,
                                                       game=discord.Game(name=self.bot.lastInGameStatus))
            await asyncio.sleep(150)  # task runs every 2.5 min (150s)
        print("--Discord Status Task loop finished--")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING MINI-CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING MINI-CLASS-->" + self.__class__.__name__ + " class called")