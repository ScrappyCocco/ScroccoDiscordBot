# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import steamapi
import time
import discord
import requests
import json

from steamapi import core
from hypixthon import Hypixthon
from botVariablesClass import BotVariables
from steamapi import user
from datetime import datetime

# ---------------------------------------------------------------------


class BotGamingCommands:
    """ Class with Bot 'Gaming' commands (statistics for gamers) """
    # ---------------------------------------------------------------------

    botVariables = BotVariables(False)  # used for 2 api keys
    client = Hypixthon(botVariables.get_hypixel_key())  # hypixel api connection
    core.APIConnection(api_key=botVariables.get_steam_key())  # steam api connection

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def ow(self, ctx, *args):
        """Print Overwatch stats of a player
        Usage:** !ow "Name-Tag" "eu(default)/us"[optional]
        """
        print("-------------------------")
        if len(args) == 0 or len(args) > 2:  # parameters aren't correct - print the correct usage of the command
            await self.bot.say("**Usage:** !ow \"Name-Tag\" eu(default)/us[optional]")
        else:
            if len(args) == 1:  # server not passed, going with default server
                ow_region = "eu"
            else:  # server passed, changing default server
                ow_region = args[1]
            name = args[0]
            url = "http://ow-api.herokuapp.com/profile/pc/" + ow_region + "/" + name
            print("OW Request:" + url)
            r = requests.get(url)
            if str(r) == "<Response [404]>":  # user not found
                await self.bot.say("Error: 404 User not found")
                return
            # creating the discord Embed response
            embed = discord.Embed(title="Overwatch Stats",
                                  colour=discord.Colour(0xefd1a0),
                                  url="http://masteroverwatch.com/profile/pc/" + ow_region + "/" + name,
                                  description="Stats of \"" + name + "\" playing in \"" + ow_region + "\"",
                                  timestamp=datetime.utcfromtimestamp(time.time())
                                  )
            if not r.json()['star'] == "":
                embed.set_image(url=str(r.json()['star']))
            embed.set_thumbnail(url=r.json()['portrait'])
            embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
            embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())

            embed.add_field(name="In-Game Name:", value=r.json()['username'])
            embed.add_field(name="Level:", value=str(r.json()['level']))
            if r.json()['competitive']["rank"] == "null":
                rank = "Not found"
            else:
                rank = r.json()['competitive']["rank"]
            embed.add_field(name="Competitive Rank:", value=rank)
            try:
                embed.add_field(name="QuickPlay Wins:", value=r.json()['games']['quickplay']['wins'])
                comp_wins = str(r.json()['games']['competitive']['wins']) + " Wins"
            except KeyError:
                print("Wins Key Error, trying with Won key...")
                embed.add_field(name="QuickPlay Wins:", value=r.json()['games']['quickplay']['won'])
                comp_wins = str(r.json()['games']['competitive']['won']) + " Wins"
            comp_tot = str(r.json()['games']['competitive']['played']) + " Played"
            embed.add_field(name="Competitive Play:", value=comp_wins + "/" + comp_tot)

            await self.bot.say(embed=embed)  # send the discord embed message with user stats
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def r6(self, ctx, *args):
        """Print Rainbow6 player's stats
        Usage: !r6 PlayerName
        """
        print("-------------------------")
        if len(args) == 0 or len(args) > 1:  # parameters aren't correct - print the correct usage of the command
            await self.bot.say("**Usage:** !r6 PlayerName")
        else:
            name = args[0]
            url_stats = "http://rainbowsix7nightbot.herokuapp.com/rainbowsix7.php?platform=uplay&nick=" + name + "&command=stats"
            url_time = "http://rainbowsix7nightbot.herokuapp.com/rainbowsix7.php?platform=uplay&nick=" + name + "&command=time"
            url_rank = "http://rainbowsix7nightbot.herokuapp.com/rainbowsix7.php?platform=uplay&nick=" + name + "&command=rank"
            # error strings
            string_compare_1 = "00h 00m 00s (ranked + casual)"
            string_compare_2 = "Couldn't retrieve 'profileId'! Maybe player doesn't exist? Check typos or manually parse the profileId found in the URL of your ubisoft profile page: https://game-rainbow6.ubi.com/"
            r1 = requests.get(url_stats)
            r2 = requests.get(url_time)
            r3 = requests.get(url_rank)
            if str(r2.text) == string_compare_1 or str(r2.text) == string_compare_2:  # An error occurred
                await self.bot.say("Error - User not found!")
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

            embed.add_field(name="Stats:", value=str(r1.text))
            embed.add_field(name="Play-Time:", value=str(r2.text))
            embed.add_field(name="Competitive Rank:", value=str(r3.text))

            await self.bot.say(embed=embed)  # send the discord embed message with user stats
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
        if len(args) == 0 or len(args) > 1:   # parameters aren't correct - print the correct usage of the command
            await self.bot.say("**Usage:** !steam PlayerID")
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
                    r = requests.get(steam_api_url)
                    if not r.json()['response']['success'] == 1:
                        await self.bot.say("Error - User not found...")
                        return
                    else:
                        user_id = int(r.json()['response']['steamid'])
                        print("SteamId64 Request:" + str(user_id))
                        steam_user = user.SteamUser(userid=user_id)
            except steamapi.errors.UserNotFoundError:  # Not an ID, but a vanity URL.
                await self.bot.say("Error - User not found...")
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
            except (steamapi.errors.APIUnauthorized, steamapi.errors.UserNotFoundError, KeyError, AttributeError):
                await self.bot.say("Error - Can't get user data!")
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
            await self.bot.say(embed=embed)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def mcskin(self, *args):
        """Print the Minecraft skin of a user
        Usage: !mcskin "MinecraftUsername"
        """
        print("-------------------------")
        if len(args) == 1:
            name = args[0]
            print("Skin Param:" + name)
            await self.bot.say("https://mcapi.ca/skin/" + name + "/300")
        else:  # parameters aren't correct - print the correct usage of the command
            await self.bot.say("**Usage:** !mcskin McName")
        print("-------------------------")

    @commands.command()
    async def mchead(self, *args):
        """Print the head of the Minecraft skin of a user
        Usage: !mchead "MinecraftUsername"
        """
        print("-------------------------")
        if len(args) == 1:
            name = args[0]
            print("param:" + name)
            await self.bot.say("https://mcapi.ca/avatar/" + name + "/100/true")
        else:  # parameters aren't correct - print the correct usage of the command
            await self.bot.say("**Usage:** !mchead McName")
        print("-------------------------")

    @commands.command()
    async def hy(self, *args):
        """Print the user's stats in the Hypixel Server
        Usage: !hy "MinecraftUsername"
        """
        print("-------------------------")
        error = False
        uuid = 0
        if len(args) == 1:
            name = args[0]
            try:
                r = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name)
                uuid = r.json()['id']  # getting the user MinecraftID
                print("Minecraft ID:" + uuid)
            except json.decoder.JSONDecodeError:
                error = True
                print("Error getting PlayerID")
                await self.bot.say("*Player not found...*")
            if not error:
                stats = self.client.getPlayer(uuid=uuid)
                final_string = "```"  # creating final string
                final_string += ("Name:" + stats['player']['displayname']) + "\n"
                final_string += ("Karma:" + str(stats['player']['karma'])) + "\n"
                try:
                    # the "timePlaying" seems to be bugged because it never change, not my fault
                    final_string += ("Time Playing:" + str(stats['player']['timePlaying'])) + "h (Bug?) \n"
                except KeyError:
                    final_string += ("Time Playing:" + "Value not found \n")
                final_string += "```"
                await self.bot.say(final_string)
        else:  # parameters aren't correct - print the correct usage of the command
            await self.bot.say("**Usage:** !hy McName")
        print("-------------------------")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotGamingCommands(bot))
