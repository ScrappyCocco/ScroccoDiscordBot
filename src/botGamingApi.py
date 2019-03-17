# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import steamapi.steamapi
import time
import discord
import os
import urllib
import requests
import json
import aiohttp
import hypixel

from urllib import request
from steamapi.steamapi import core
from botMethodsClass import BotMethods
from steamapi.steamapi import user
from datetime import datetime
from howlongtobeatpy import HowLongToBeat


# ---------------------------------------------------------------------


class BotGamingCommands:
    """ Class with Bot 'Gaming' commands (statistics for gamers) """
    # ---------------------------------------------------------------------

    # list of class essential variables, the None variables are assigned in the constructor because i need the bot reference
    botVariables = None  # used for 2 api keys
    command_prefix = None
    steam_game_list_json = None  # instance the steam json as empty, used in "steamgame" command

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
        Usage: !r6 PlayerName Platform(xone/ps4/uplay)
        Example: !r6 Player1 psn
        Example: !r6 Player2 uplay
        """
        print("-------------------------")
        if len(args) == 0 or len(args) > 2:  # parameters aren't correct - print the correct usage of the command
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "r6 PlayerName Platform, see " + self.command_prefix + "help r6 for more")
        else:
            if len(args) == 2:
                platform_string = str(args[1]).lower()
                if platform_string != "xone" and platform_string != "ps4" and platform_string != "uplay":
                    await self.bot.send_message(ctx.message.channel,
                                                "Platform not correct - options: 'xone', 'ps4' or 'uplay'")
                    return
            else:
                platform_string = "uplay"  # default platform is uplay
            # temporary message to tell the user to wait
            temp_message = await self.bot.send_message(ctx.message.channel,
                                                       "*Downloading your player stats, give me a second*")
            player_name_string = args[0]
            url_stats = "https://api.r6stats.com/api/v1/players/" + player_name_string + "?platform=" + platform_string
            url_operators = "https://api.r6stats.com/api/v1/players/" + player_name_string + "/operators?platform=" + platform_string
            # first request, check for errors
            print("R6 - Starting First Request")
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url_stats) as resp:
                        request_player_stats = await resp.json()
                if 'status' in request_player_stats:  # an error occurred looking for the player
                    print("R6 - Player does not exist")
                    await self.bot.send_message(ctx.message.channel, "*No player found with that name...*")
                    await self.bot.delete_message(temp_message)
                    return
                print("R6 - No errors downloading the players, downloading other data...")
                async with aiohttp.ClientSession() as session:
                    async with session.get(url_operators) as resp:
                        request_player_operators = await resp.json()
            except (json.JSONDecodeError, aiohttp.ClientResponseError):
                print("R6 - Error downloading the data")
                await self.bot.send_message(ctx.message.channel,
                                            "An error occurred requesting your data, please retry later... (api.r6stats.com error)")
                return
            print("R6 - Download completed, creating the embed")
            # creating the discord Embed response
            embed = discord.Embed(title="Rainbow6 Stats Link",
                                  colour=discord.Colour(0x007bb5),
                                  url="https://r6stats.com/stats/" + platform_string + "/" + player_name_string,
                                  description="Stats of \"" + player_name_string + "\", updated at:" + str(
                                      request_player_stats['player']['updated_at']),
                                  timestamp=datetime.utcfromtimestamp(time.time())
                                  )
            embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
            embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())
            # --- ranked stats ---
            ranked_stats_string = "Empty"
            ranked_playtime = 0
            if request_player_stats['player']['stats']['ranked']['has_played']:
                ranked_playtime = "{0:0.1f}".format(
                    request_player_stats['player']['stats']['ranked']['playtime'] / 3600)
                ranked_stats_string = str(
                    "{:,}".format(request_player_stats['player']['stats']['ranked']['wins'])) + " wins, "
                ranked_stats_string += str(
                    "{:,}".format(request_player_stats['player']['stats']['ranked']['losses'])) + " losses, "
                ranked_stats_string += str(
                    "{:,}".format(request_player_stats['player']['stats']['ranked']['kills'])) + " kills, "
                ranked_stats_string += str(
                    "{:,}".format(request_player_stats['player']['stats']['ranked']['deaths'])) + " deaths"
            embed.add_field(name="Ranked Stats (during " + str(ranked_playtime) + "h):", value=str(ranked_stats_string),
                            inline=False)
            # --- casual stats ---
            casual_stats_string = "Empty"
            casual_playtime = 0
            if request_player_stats['player']['stats']['casual']['has_played']:
                casual_playtime = "{0:0.1f}".format(
                    request_player_stats['player']['stats']['casual']['playtime'] / 3600)
                casual_stats_string = str(
                    "{:,}".format(request_player_stats['player']['stats']['casual']['wins'])) + " wins, "
                casual_stats_string += str(
                    "{:,}".format(request_player_stats['player']['stats']['casual']['losses'])) + " losses, "
                casual_stats_string += str(
                    "{:,}".format(request_player_stats['player']['stats']['casual']['kills'])) + " kills, "
                casual_stats_string += str(
                    "{:,}".format(request_player_stats['player']['stats']['casual']['deaths'])) + " deaths"
            embed.add_field(name="Casual Stats (during " + str(casual_playtime) + "h):", value=str(casual_stats_string),
                            inline=False)
            # --- overall stats ---
            overall_stats_string = "Lv." + str(request_player_stats['player']['stats']['progression']['level']) + " - "
            overall_stats_string += str(
                "{:,}".format(request_player_stats['player']['stats']['overall']['revives'])) + " revives, "
            overall_stats_string += str(
                "{:,}".format(request_player_stats['player']['stats']['overall']['suicides'])) + " suicides, "
            overall_stats_string += str("{:,}".format(
                request_player_stats['player']['stats']['overall']['steps_moved'])) + " steps moved \n"
            overall_stats_string += str("{:,}".format(
                request_player_stats['player']['stats']['overall']['bullets_fired'])) + " bullets fired, "
            overall_stats_string += str("{:,}".format(
                request_player_stats['player']['stats']['overall']['bullets_hit'])) + " bullets hit, "
            overall_stats_string += str("{:,}".format(
                request_player_stats['player']['stats']['overall']['headshots'])) + " headshots, "
            overall_stats_string += str(
                "{:,}".format(request_player_stats['player']['stats']['overall']['assists'])) + " assists"
            embed.add_field(name="Overall Player Stats", value=str(overall_stats_string), inline=False)
            # --- most played ark operator ---
            best_atk_index = BotMethods.get_most_played_operator_index(request_player_operators['operator_records'],
                                                                       True)
            if best_atk_index >= 0:
                best_ark_operator_name = str(
                    request_player_operators['operator_records'][best_atk_index]['operator']['ctu']) + " - " + str(
                    request_player_operators['operator_records'][best_atk_index]['operator']['name'])
                best_atk_operator_time = str("{0:0.1f}".format(
                    request_player_operators['operator_records'][best_atk_index]['stats']['playtime'] / 3600)) + "h"
                best_ark_operator_string = str("{:,}".format(
                    request_player_operators['operator_records'][best_atk_index]['stats']['wins'])) + " wins, "
                best_ark_operator_string += str("{:,}".format(
                    request_player_operators['operator_records'][best_atk_index]['stats']['losses'])) + " losses, "
                best_ark_operator_string += str("{:,}".format(
                    request_player_operators['operator_records'][best_atk_index]['stats']['kills'])) + " kills, "
                best_ark_operator_string += str("{:,}".format(
                    request_player_operators['operator_records'][best_atk_index]['stats']['deaths'])) + " deaths"
            else:
                best_ark_operator_string = "Unknown"
                best_ark_operator_name = "Not Found"
                best_atk_operator_time = "0h"
            embed.add_field(
                name="Stats about most played attack operator: " + best_ark_operator_name + " (" + best_atk_operator_time + ")",
                value=str(best_ark_operator_string), inline=False)
            # --- most played def operator ---
            best_def_index = BotMethods.get_most_played_operator_index(request_player_operators['operator_records'],
                                                                       False)
            if best_def_index >= 0:
                best_def_operator_name = str(
                    request_player_operators['operator_records'][best_def_index]['operator']['ctu']) + " - " + str(
                    request_player_operators['operator_records'][best_def_index]['operator']['name'])
                best_def_operator_time = str("{0:0.1f}".format(
                    request_player_operators['operator_records'][best_def_index]['stats']['playtime'] / 3600)) + "h"
                best_def_operator_string = str("{:,}".format(
                    request_player_operators['operator_records'][best_def_index]['stats']['wins'])) + " wins, "
                best_def_operator_string += str("{:,}".format(
                    request_player_operators['operator_records'][best_def_index]['stats']['losses'])) + " losses, "
                best_def_operator_string += str("{:,}".format(
                    request_player_operators['operator_records'][best_def_index]['stats']['kills'])) + " kills, "
                best_def_operator_string += str("{:,}".format(
                    request_player_operators['operator_records'][best_def_index]['stats']['deaths'])) + " deaths"
            else:
                best_def_operator_string = "Unknown"
                best_def_operator_name = "Not Found"
                best_def_operator_time = "0h"
            embed.add_field(
                name="Stats about most played defense operator: " + best_def_operator_name + " (" + best_def_operator_time + ")",
                value=str(best_def_operator_string), inline=False)
            # send the discord embed message with user stats
            await self.bot.delete_message(temp_message)
            await self.bot.send_message(ctx.message.channel, embed=embed)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def steam(self, ctx, *args):
        """Print the user Steam Profile (MAY NOT WORK AFTER NEW STEAM PRIVACY SETTINGS)
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
                    print("SteamId64 Request With User ID (Int)")
                    steam_user = user.SteamUser(userid=user_id)
                else:
                    # i need to get the SteamID from the Username
                    print("SteamIdURL Request With User ID (Str)")
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
                        print("SteamId64 Request Started")
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
            except (steamapi.steamapi.errors.APIUnauthorized, steamapi.steamapi.errors.UserNotFoundError, KeyError,
                    AttributeError):
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

    # Little class used to store games in array
    class SteamGame(object):
        app_id = ""
        app_name = ""
        similar = 0

        def __init__(self, appid: str, name: str, similar: float):
            self.app_id = appid
            self.app_name = name
            self.similar = similar

    @commands.command(pass_context=True)
    async def steamgame(self, ctx, *args):
        """Print the informations about a steam game
        Usage: !steamgame "Portal 2"
        """
        if len(args) == 1:
            game_name = args[0].strip().lower()
            game_name_numbers = [int(s) for s in game_name.split() if s.isdigit()]
            steam_apps_url = "http://api.steampowered.com/ISteamApps/GetAppList/v2"
            steam_apps_page = "http://store.steampowered.com/api/appdetails?appids="
            current_players_info = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid="
            # temporary message to tell the user to wait
            temp_message = await self.bot.send_message(ctx.message.channel, "*Game search started, give me a second*")
            print("-------------------------")
            if self.steam_game_list_json is None:  # is the json cached?
                print("SteamGameList: Start downloading steam apps json, no cached version found")
                async with aiohttp.ClientSession() as session:  # request all steam games
                    async with session.get(steam_apps_url) as resp:
                        self.steam_game_list_json = await resp.json()
                print("SteamGameList: Download completed!")
            else:
                print("SteamGameList: json file already downloaded, using cached version...")
            games_found = []
            max_prob = 0.0
            for entry in self.steam_game_list_json['applist']['apps']:  # for each steam game
                prob = BotMethods.similar(game_name, entry['name'].lower(),
                                          game_name_numbers)  # calculate the name similarity
                # compare lower() strings, because i don't mind if the name is uppercase or not
                if prob > 0.7:  # consider it only if it's > 0.7 (range is 0.0-1.0)
                    games_found.append(
                        self.SteamGame(entry['appid'], entry['name'], prob))  # store that game in the array
                    if prob > max_prob:  # search for max prob
                        max_prob = prob
                        if prob >= 1.0:  # i have found the perfect string
                            print("Perfect name found, search cycle stopped")
                            break  # stop the for
            if len(games_found) > 0:  # i have found at least one possible game
                game_app_id = ""
                for game in games_found:  # search the game with the max name similarity in the array
                    if game.similar == max_prob:
                        print("Game Chosen: " + game.app_name + " - Appid:" + str(game.app_id) + " - Sim.:" + str(
                            max_prob))
                        game_app_id = game.app_id  # get the game id
                        break
                # make 2 request to get all necessary game informations
                async with aiohttp.ClientSession() as session:
                    async with session.get(steam_apps_page + str(game_app_id)) as resp:
                        request_app_page = await resp.json()
                async with aiohttp.ClientSession() as session:
                    async with session.get(current_players_info + str(game_app_id)) as resp:
                        request_app_players = await resp.json()
                # create the final message
                if not request_app_page[str(game_app_id)]['success']:
                    print("Game Info Request returned success:False")
                    await self.bot.delete_message(temp_message)
                    await self.bot.send_message(ctx.message.channel,
                                                "*Cannot get informations about this game, sorry...*")
                    return
                embed = discord.Embed(title=str(request_app_page[str(game_app_id)]['data']['name']),
                                      colour=discord.Colour(0x000080),
                                      url="http://store.steampowered.com/app/" + str(game_app_id) + "/",
                                      description="Steam statistics about the game: \"" + str(
                                          request_app_page[str(game_app_id)]['data']['name']) + "\"",
                                      timestamp=datetime.utcfromtimestamp(time.time())
                                      )
                embed.set_thumbnail(url=str(request_app_page[str(game_app_id)]['data']['header_image']))
                embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
                embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())
                # --- price field, get the price or put "Unknown" ---
                if 'price_overview' in request_app_page[str(game_app_id)]['data']:
                    price_string = str(request_app_page[str(game_app_id)]['data']['price_overview']['final'])
                    price_currency = str(request_app_page[str(game_app_id)]['data']['price_overview']['currency'])
                    price_string = price_string[:(len(price_string) - 2)] + "." + price_string[
                                                                                  (len(
                                                                                      price_string) - 2):] + price_currency
                    if 'discount_percent' in request_app_page[str(game_app_id)]['data']['price_overview'] \
                            and request_app_page[str(game_app_id)]['data']['price_overview']['discount_percent'] > 0:
                        price_string += " (" + str(
                            request_app_page[str(game_app_id)]['data']['price_overview']['discount_percent']) + "% off)"
                else:
                    price_string = "Unknown"
                embed.add_field(name="Price", value=str(price_string))
                # --- metacritic field, get the metacritic score or put "Unknown" ---
                if 'metacritic' in request_app_page[str(game_app_id)]['data']:
                    metacritic_score = str(request_app_page[str(game_app_id)]['data']['metacritic']['score'])
                else:
                    metacritic_score = "Unknown"
                embed.add_field(name="Metacritic Score", value=str(metacritic_score))
                # --- release date field, get the release date or put "Coming Soon" ---
                if request_app_page[str(game_app_id)]['data']['release_date']['coming_soon']:
                    release_date = "Coming Soon"
                else:
                    release_date = str(request_app_page[str(game_app_id)]['data']['release_date']['date'])
                embed.add_field(name="Release Date", value=str(release_date))
                # --- developers field, get the list of the developers ---
                developers = ""
                for dev in request_app_page[str(game_app_id)]['data']['developers']:
                    developers += str(dev) + "\n"
                embed.add_field(name="Developers", value=str(developers))
                # --- number of achievements ---ù
                if 'achievements' in request_app_page[str(game_app_id)]['data']:
                    embed.add_field(name="Achievements",
                                    value=str(request_app_page[str(game_app_id)]['data']['achievements']['total']))
                else:
                    embed.add_field(name="Achievements", value="Unknown")
                # --- players field, get the number of current players in that game ---
                if 'player_count' in request_app_players['response']:
                    current_players = str("{:,}".format(request_app_players['response']['player_count']))
                else:
                    current_players = "Unknown"
                embed.add_field(name="Current Players", value=str(current_players))
                # --- list of game tags ---
                game_tags = ""
                for tag in request_app_page[str(game_app_id)]['data']['genres']:
                    game_tags += str(tag['description']) + ", "
                embed.add_field(name="Genres", value=str(game_tags[:-2]))
                # --- sending the message ---
                await self.bot.delete_message(temp_message)
                await self.bot.send_message(ctx.message.channel, embed=embed)
            else:
                print("No games found")
                await self.bot.delete_message(temp_message)
                await self.bot.send_message(ctx.message.channel, "*No games found, check the name...*")
            print("-------------------------")
        else:
            await self.bot.send_message(ctx.message.channel, "**Usage:** " + self.command_prefix + "steamgame GameName")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def mcskin(self, ctx, *args):
        """Print the Minecraft skin of a user
        Usage: !mcskin "MinecraftUsername"
        """
        print("-------------------------")
        if len(args) == 1:
            name = args[0]
            uuid = await BotMethods.get_player_minecraft_uuid(name)
            if uuid is None:
                print("Error getting PlayerID")
                await self.bot.send_message(ctx.message.channel, "*Player not found...*")
            else:
                # download the minecraft image
                print("mcskin: Downloading file...")
                urllib.request.urlretrieve("https://crafatar.com/renders/body/" + uuid, uuid + ".png")
                print("mcskin: Sending file...")
                # send the minecraft image as file
                try:
                    await self.bot.send_file(ctx.message.channel, uuid + ".png")
                except discord.HTTPException:
                    await self.bot.send_message(ctx.message.channel,
                                                "*Something went wrong sending your Minecraft skin image...*")
                # now delete the downloaded file
                os.remove(uuid + ".png")
                print("mcskin: File sent and deleted")
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
            uuid = await BotMethods.get_player_minecraft_uuid(name)
            if uuid is None:
                print("Error getting PlayerID")
                await self.bot.send_message(ctx.message.channel, "*Player not found...*")
            else:
                # download the minecraft image
                print("mchead: Downloading file...")
                urllib.request.urlretrieve("https://crafatar.com/renders/head/" + uuid, uuid + ".png")
                print("mchead: Sending file...")
                # send the minecraft image as file
                try:
                    await self.bot.send_file(ctx.message.channel, uuid + ".png")
                except discord.HTTPException:
                    await self.bot.send_message(ctx.message.channel,
                                                "*Something went wrong sending your Minecraft skin image...*")
                # now delete the downloaded file
                os.remove(uuid + ".png")
                print("mchead: File sent and deleted")
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
        player = None
        if len(args) == 1:
            name = args[0]
            uuid = await BotMethods.get_player_minecraft_uuid(name)
            if uuid is None:
                error = True
                print("Error getting PlayerID")
                await self.bot.send_message(ctx.message.channel, "*Player not found...*")
            else:
                player = hypixel.Player(uuid)
            if not error and player is not None:
                # creating final embed
                first_login_epoch_timestamp = (int(str(player.getPlayerInfo()['firstLogin']))) / 1000
                last_login_epoch_timestamp = (int(str(player.getPlayerInfo()['lastLogin']))) / 1000
                embed = discord.Embed(title="Hypixel stats - " + str(player.getName()),
                                      colour=discord.Colour(0xAD7514),
                                      url="https://hypixel.net/player/" + str(player.getName()) + "/",
                                      description="A bit of Hypixel stats, click the link above for more",
                                      timestamp=datetime.utcfromtimestamp(time.time())
                                      )
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/396666575081439243/445599418456997898/image.png")
                embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
                embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())
                embed.add_field(name="Name", value=str(player.getName()))
                embed.add_field(name="Rank", value=str(player.getRank()['rank']))
                embed.add_field(name="Level", value=str(player.getLevel()))
                embed.add_field(name="Karma", value=str(player.JSON['karma']))
                embed.add_field(name="First Login",
                                value=str(time.strftime('%d\\%m\\%Y %H:%M:%S', time.gmtime(first_login_epoch_timestamp))))
                embed.add_field(name="Last Login",
                                value=str(time.strftime('%d\\%m\\%Y %H:%M:%S', time.gmtime(last_login_epoch_timestamp))))
                await self.bot.send_message(ctx.message.channel, embed=embed)
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
                print("SteamIdURL Request Started")
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
                    print("SteamId64 Request Started")
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

    @commands.command(pass_context=True)
    async def time(self, ctx, *args):
        """Print the time to complete a game from howlongtobeat
        Usage: !time "game name"
        Example !time "awesome game"
        """
        if len(args) == 0 or len(args) > 1:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "time \"game name\", see " + self.command_prefix + "help time for more")
        else:
            results_list = await HowLongToBeat().async_search(args[0])
            if results_list is not None and len(results_list) > 0:
                max_sim = -1
                best_element = None
                for element in results_list:
                    if element.similarity > max_sim:
                        max_sim = element.similarity
                        best_element = element
                embed = discord.Embed(title="HowLongToBeat details about " + str(best_element.game_name),
                                      colour=discord.Colour(0x000000),
                                      url=str(best_element.game_web_link),
                                      description="Details about how long is to complete the game " + str(
                                          best_element.game_name) + " playing in different ways",
                                      timestamp=datetime.utcfromtimestamp(time.time())
                                      )
                embed.set_thumbnail(
                    url=str(best_element.game_image_url))
                embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
                embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())
                if best_element.gameplay_main_label is not None:  # Check if the name is available first
                    if best_element.gameplay_main_unit is None:  # Then check if the time is available
                        embed.add_field(name=str(best_element.gameplay_main_label), value="Not available...",
                                        inline=False)
                    else:
                        embed.add_field(name=str(best_element.gameplay_main_label),
                                        value=(str(best_element.gameplay_main) + " " + str(
                                            best_element.gameplay_main_unit)),
                                        inline=False)
                if best_element.gameplay_main_extra_label is not None:  # Check if the name is available first
                    if best_element.gameplay_main_extra_unit is None:  # Then check if the time is available
                        embed.add_field(name=str(best_element.gameplay_main_extra_label), value="Not available...",
                                        inline=False)
                    else:
                        embed.add_field(name=str(best_element.gameplay_main_extra_label),
                                        value=(str(best_element.gameplay_main_extra) + " " + str(
                                            best_element.gameplay_main_extra_unit)),
                                        inline=False)
                if best_element.gameplay_completionist_label is not None:  # Check if the name is available first
                    if best_element.gameplay_completionist_unit is None:  # Then check if the time is available
                        embed.add_field(name=str(best_element.gameplay_completionist_label), value="Not available...",
                                        inline=False)
                    else:
                        embed.add_field(name=str(best_element.gameplay_completionist_label),
                                        value=(str(best_element.gameplay_completionist) + " " + str(
                                            best_element.gameplay_completionist_unit)),
                                        inline=False)
                await self.bot.send_message(ctx.message.channel, embed=embed)
            else:
                await self.bot.send_message(ctx.message.channel, "Looks like i've not found anything :(")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot
        self.botVariables = self.bot.bot_variables_reference
        # assigning variables value now i can use botVariables
        hypixel.setKeys([self.botVariables.get_hypixel_key()])  # This sets the API keys that are going to be used.
        core.APIConnection(api_key=self.botVariables.get_steam_key())  # steam api connection
        self.command_prefix = self.botVariables.command_prefix

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotGamingCommands(bot))
