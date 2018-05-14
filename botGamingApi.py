# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import steamapi.steamapi
import time
import discord
import requests
import json
import aiohttp

from hypixel_py import hypixel
from steamapi.steamapi import core
from botVariablesClass import BotVariables
from botMethodsClass import BotMethods
from steamapi.steamapi import user
from datetime import datetime


# ---------------------------------------------------------------------


class BotGamingCommands:
    """ Class with Bot 'Gaming' commands (statistics for gamers) """
    # ---------------------------------------------------------------------

    botVariables = BotVariables(False)  # used for 2 api keys
    hypixel.setKeys(botVariables.get_hypixel_key())  # This sets the API keys that are going to be used.
    core.APIConnection(api_key=botVariables.get_steam_key())  # steam api connection
    command_prefix = botVariables.command_prefix

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def ow(self, ctx, *args):
        """Print Overwatch stats of a player
        Usage:** !ow "Name-Tag" "eu(default)/us"[optional]
        """
        print("-------------------------")
        if len(args) == 0 or len(args) > 2:  # parameters aren't correct - print the correct usage of the command
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "ow \"Name-Tag\" eu(default)/us[optional]")
        else:
            if len(args) == 1:  # server not passed, going with default server
                ow_region = "eu"
            else:  # server passed, changing default server
                ow_region = args[1]
            name = args[0]
            name = name.replace("#", "-", 1)
            url = "http://ow-api.herokuapp.com/profile/pc/" + ow_region + "/" + name
            print("OW Request:" + url)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    r_text = await resp.text()
                    # r = requests.get(url)
                    if str(r_text) == "<Response [404]>" or str(r_text) == "Not Found":  # user not found
                        await self.bot.send_message(ctx.message.channel, "Error: 404 User not found")
                        return
                    r = await resp.json()
            # creating the discord Embed response
            embed = discord.Embed(title="Overwatch Stats",
                                  colour=discord.Colour(0xefd1a0),
                                  url="http://masteroverwatch.com/profile/pc/" + ow_region + "/" + name,
                                  description="Stats of \"" + name + "\" playing in \"" + ow_region + "\"",
                                  timestamp=datetime.utcfromtimestamp(time.time())
                                  )
            if r['star'] != "":
                embed.set_image(url=str(r['star']))
            embed.set_thumbnail(url=r['portrait'])
            embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
            embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())

            embed.add_field(name="In-Game Name:", value=r['username'])
            embed.add_field(name="Level:", value=str(r['level']))
            if r['competitive']["rank"] == "null":
                rank = "Not found"
            else:
                rank = r['competitive']["rank"]
            embed.add_field(name="Competitive Rank:", value=rank)
            try:
                embed.add_field(name="QuickPlay Wins:", value=r['games']['quickplay']['wins'])
                comp_wins = str(r['games']['competitive']['wins']) + " Wins"
            except KeyError:
                print("Wins Key Error, trying with Won key...")
                embed.add_field(name="QuickPlay Wins:", value=r['games']['quickplay']['won'])
                comp_wins = str(r['games']['competitive']['won']) + " Wins"
            comp_tot = str(r['games']['competitive']['played']) + " Played"
            embed.add_field(name="Competitive Play:", value=comp_wins + "/" + comp_tot)
            # send the discord embed message with user stats
            await self.bot.send_message(ctx.message.channel, embed=embed)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def r6(self, ctx, *args):
        """Print Rainbow6 player's stats
        Usage: !r6 PlayerName Platform
        Example: !r6 Player1 psn
        Example: !r6 Player2 uplay
        """
        print("-------------------------")
        if len(args) == 0 or len(args) > 2:  # parameters aren't correct - print the correct usage of the command
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "r6 PlayerName Platform, see " + self.command_prefix + "help r6 for more")
        else:
            if len(args) == 2:
                platform = str(args[1]).lower()
                if platform != "xbl" and platform != "psn" and platform != "uplay":
                    await self.bot.send_message(ctx.message.channel,
                                                "Platform not correct - options: 'xbl', 'psn' or 'uplay'")
                    return
            else:
                platform = "uplay"
            name = args[0]
            url_stats = "http://rainbowsix7nightbot.herokuapp.com/rainbowsix7.php?platform=" + platform + "&nick=" + name + "&command=stats"
            url_time = "http://rainbowsix7nightbot.herokuapp.com/rainbowsix7.php?platform=" + platform + "&nick=" + name + "&command=time"
            url_rank = "http://rainbowsix7nightbot.herokuapp.com/rainbowsix7.php?platform=" + platform + "&nick=" + name + "&command=rank"
            # error strings
            string_compare_1 = "00h 00m 00s (ranked + casual)"
            string_compare_2 = "Couldn't retrieve 'profileId'! Maybe player doesn't exist? Check typos or manually parse the profileId found in the URL of your ubisoft profile page: https://game-rainbow6.ubi.com/"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url_stats) as resp:
                        r1 = await resp.text()
                    async with session.get(url_time) as resp:
                        r2 = await resp.text()
                    async with session.get(url_rank) as resp:
                        r3 = await resp.text()
            except aiohttp.client_exceptions.ServerDisconnectedError:
                print("R6 request failed")
                await self.bot.send_message(ctx.message.channel, "*Can't retrieve R6 user data...*")
                return
            print("R6 request completed")
            if str(r2) == string_compare_1 or str(r2) == string_compare_2:  # An error occurred
                await self.bot.send_message(ctx.message.channel, "Error - User not found!")
                return
            # creating the discord Embed response
            embed = discord.Embed(title="Rainbow6 Stats",
                                  colour=discord.Colour(0x007bb5),
                                  url="https://r6stats.com/",
                                  description="Stats of \"" + name + "\"",
                                  timestamp=datetime.utcfromtimestamp(time.time())
                                  )
            embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
            embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())

            embed.add_field(name="Stats:", value=str(r1))
            embed.add_field(name="Play-Time:", value=str(r2))
            embed.add_field(name="Competitive Rank:", value=str(r3))
            # send the discord embed message with user stats
            await self.bot.send_message(ctx.message.channel, embed=embed)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def steam(self, ctx, *args):
        """Print the user Steam Profile
        Usage: !steam "UserID"
        Example: !steam ScrappyEnterprise
        """
        print("-------------------------")
        is_integer = False
        print("Steam:Arguments:" + str(len(args)))
        if len(args) == 0 or len(args) > 1:  # parameters aren't correct - print the correct usage of the command
            await self.bot.send_message(ctx.message.channel, "**Usage:** " + self.command_prefix + "steam PlayerID")
        else:
            username = args[0]
            try:
                user_id = int(username)
                is_integer = True
            except ValueError:  # Not an ID, but a vanity URL.
                user_id = username
            try:
                if is_integer:  # convert it
                    print("SteamId64 Request:" + str(user_id))
                    steam_user = user.SteamUser(userid=user_id)
                else:
                    # i need to get the SteamID from the Username
                    print("SteamIdURL Request:" + str(user_id))
                    steam_api_key = self.botVariables.get_steam_key()
                    steam_api_url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
                    steam_api_url += "?key=" + steam_api_key + "&vanityurl=" + str(user_id)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(steam_api_url) as resp:
                            r = await resp.json()
                    if r['response']['success'] != 1:
                        await self.bot.send_message(ctx.message.channel, "Error - User not found...")
                        return
                    else:
                        user_id = int(r['response']['steamid'])
                        print("SteamId64 Request:" + str(user_id))
                        steam_user = user.SteamUser(userid=user_id)
            except steamapi.steamapi.errors.UserNotFoundError:  # Not an ID, but a vanity URL.
                await self.bot.send_message(ctx.message.channel, "Error - User not found...")
                return
            # now i have the username, let's create the reply
            try:
                name = steam_user.name
                friends = len(steam_user.friends)
                games = len(steam_user.games)
                img = steam_user.avatar_full
                medals = len(steam_user.badges)
                profile_url = steam_user.profile_url
                level = steam_user.level
            except (steamapi.steamapi.errors.APIUnauthorized, steamapi.steamapi.errors.UserNotFoundError, KeyError, AttributeError):
                await self.bot.send_message(ctx.message.channel, "Error - Can't get user data!")
                return
            # create the final message
            embed = discord.Embed(title="Go To Steam Profile",
                                  colour=discord.Colour(0x000080),
                                  url=profile_url,
                                  description="Steam Profile Of \"" + name + "\"",
                                  timestamp=datetime.utcfromtimestamp(time.time())
                                  )
            embed.set_thumbnail(url=img)
            embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
            embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())

            embed.add_field(name="Level:", value=str(level))
            embed.add_field(name="Games:", value=str(games))
            embed.add_field(name="Friends:", value=str(friends))
            embed.add_field(name="Badges:", value=str(medals))
            if str(steam_user.currently_playing) == "None":
                playing = "Not in Game"
            else:
                playing = str(steam_user.currently_playing)
            embed.add_field(name="In-Game:", value=playing)

            recently = ""
            for SteamGame in steam_user.recently_played:
                if SteamGame is not None:
                    recently += str(SteamGame) + "\n"

            embed.add_field(name="Recent Activity:", value=recently)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def mcskin(self, ctx, *args):
        """Print the Minecraft skin of a user
        Usage: !mcskin "MinecraftUsername"
        """
        print("-------------------------")
        if len(args) == 1:
            name = args[0]
            print("Skin Param:" + name)
            await self.bot.send_message(ctx.message.channel, "https://mcapi.ca/skin/" + name + "/300")
        else:  # parameters aren't correct - print the correct usage of the command
            await self.bot.send_message(ctx.message.channel, "**Usage:** " + self.command_prefix + "mcskin McName")
        print("-------------------------")

    @commands.command(pass_context=True)
    async def mchead(self, ctx, *args):
        """Print the head of the Minecraft skin of a user
        Usage: !mchead "MinecraftUsername"
        """
        print("-------------------------")
        if len(args) == 1:
            name = args[0]
            print("param:" + name)
            await self.bot.send_message(ctx.message.channel, "https://mcapi.ca/avatar/" + name + "/100/true")
        else:  # parameters aren't correct - print the correct usage of the command
            await self.bot.send_message(ctx.message.channel, "**Usage:** " + self.command_prefix + "mchead McName")
        print("-------------------------")

    @commands.command(pass_context=True)
    async def hy(self, ctx, *args):
        """Print the user's stats in the Hypixel Server
        Usage: !hy "MinecraftUsername"
        """
        print("-------------------------")
        error = False
        uuid = 0
        if len(args) == 1:
            name = args[0]
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://api.mojang.com/users/profiles/minecraft/" + name) as resp:
                        r = await resp.json()
                uuid = r['id']  # getting the user MinecraftID
                print("Minecraft ID:" + uuid)
            except json.decoder.JSONDecodeError:
                error = True
                print("Error getting PlayerID")
                await self.bot.send_message(ctx.message.channel, "*Player not found...*")
            if not error:
                stats = self.client.getPlayer(uuid=uuid)
                final_string = "```"  # creating final string
                final_string += ("Name:" + stats['player']['displayname']) + "\n"
                final_string += ("Karma:" + str(stats['player']['karma'])) + "\n"
                try:
                    # the "timePlaying" seems to be bugged because it never change, not my fault
                    final_string += ("Time Playing:" + str(stats['player']['timePlaying'])) + "h (Bugged?) \n"
                except KeyError:
                    final_string += ("Time Playing:" + "Value not found \n")
                final_string += "```"
                await self.bot.send_message(ctx.message.channel, final_string)
        else:  # parameters aren't correct - print the correct usage of the command
            await self.bot.send_message(ctx.message.channel, "**Usage:** " + self.command_prefix + "hy McName")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def rl(self, ctx, *args):
        """Print the user's rocket league stats in an image
        Usage: !rl "Steam64ID/PSN Username/Xbox GamerTag or XUID" "Steam/Ps4/Xbox"(Optional)
        """
        if len(args) == 0:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "rl SteamID, see " + self.command_prefix + "help rl for more")
            return
        if len(args) == 1 and str(self.botVariables.get_rocket_league_platform()) == "Steam":
            is_integer = False
            username = args[0]
            try:
                user_id = int(username)
                is_integer = True
            except ValueError:  # Not an ID, but a vanity URL.
                user_id = username
            if not is_integer:  # convert the name to a steam 64 ID
                print("SteamIdURL Request:" + str(user_id))
                steam_api_key = self.botVariables.get_steam_key()
                steam_api_url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
                steam_api_url += "?key=" + steam_api_key + "&vanityurl=" + str(user_id)
                async with aiohttp.ClientSession() as session:
                    async with session.get(steam_api_url) as resp:
                        r = await resp.json()
                if r['response']['success'] != 1:
                    await self.bot.send_message(ctx.message.channel,
                                                "Error - Steam User not found... Check your steamID")
                    return
                else:
                    user_id = int(r['response']['steamid'])
                    print("SteamId64 Request:" + str(user_id))
        else:  # steam is not the default platform, get the username
            user_id = args[0]
        # now i have the steam id or the username, let's make the api-request
        request_header = {'Authorization': self.botVariables.get_rocket_league_key()}
        default_platform = self.botVariables.get_rocket_league_platform()
        platform_number = str(BotMethods.platform_to_number(default_platform))
        if len(args) == 1:  # use default platform
            request_url = "https://api.rocketleaguestats.com/v1/player?unique_id=" + str(
                user_id) + "&platform_id=" + platform_number
            r = requests.get(request_url, headers=request_header)  # make the request with header auth
        else:  # check the platform
            platform_number = str(BotMethods.platform_to_number(str(args[1])))
            if platform_number != str(-1):
                request_url = "https://api.rocketleaguestats.com/v1/player?unique_id=" + str(
                    user_id) + "&platform_id=" + platform_number
                r = requests.get(request_url, headers=request_header)  # make the request with header auth
            else:
                await self.bot.send_message(ctx.message.channel,
                                            "Platform not found, check " + self.command_prefix + "help rl")
                return
        try:
            request_result = r.json()  # try convert the request result to json
        except json.JSONDecodeError:
            await self.bot.send_message(ctx.message.channel, "Error getting the image... contact the bot owner ")
            return
        try:
            await self.bot.send_message(ctx.message.channel, request_result['signatureUrl'])
        except KeyError:
            await self.bot.send_message(ctx.message.channel,
                                        "Error getting the image... check " + self.command_prefix + "help rl ")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotGamingCommands(bot))
