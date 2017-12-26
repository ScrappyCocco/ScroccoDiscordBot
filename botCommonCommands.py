# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import html
import json
import random
import discord
import requests
import goslate
import time
import urllib.parse
import aiohttp

from discord.errors import HTTPException
from urllib import error
from datetime import datetime
from random import randint
from botVariablesClass import BotVariables
from botMethodsClass import BotMethods


# ---------------------------------------------------------------------


class BotCommonCommands:
    """ Class with Bot 'Common' commands (simple commands, for example cat or gif) """
    # ---------------------------------------------------------------------

    botVariables = BotVariables(False)  # used for username and for emoji array
    gs = goslate.Goslate()  # translator
    command_prefix = botVariables.command_prefix

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def gif(self, ctx, *args):
        """Return a random gif (with 0 or more params)
        Usage: !gif x1 x2 x3[Optional]
        Example: !gif or !gif funny cat
        """
        print("-------------------------")
        currentgifkey = self.botVariables.get_gif_key()
        print("GifRequest:Arguments:" + str(len(args)))
        tag = ""
        if len(args) == 0:
            print("Gif Request with No arguments")
            url = "http://api.giphy.com/v1/gifs/random?api_key=" + currentgifkey
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    r = await resp.json()
            await self.bot.send_message(ctx.message.channel, r['data']['image_url'])
        else:
            for x in range(0, len(args)):
                tag = tag + args[x]
                if x != (len(args) - 1):
                    tag += " "
            tag = urllib.parse.quote(tag)
            url = "http://api.giphy.com/v1/gifs/random?api_key=" + currentgifkey + "&tag=" + tag
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    r = await resp.json()
            print("GifRequest:Found Length:" + str(len(r['data'])))
            if (len(r['data'])) == 0:
                await self.bot.send_message(ctx.message.channel, "No GIF found with those tags :frowning: ")
            else:
                await self.bot.send_message(ctx.message.channel, r['data']['image_url'])
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def cat(self, ctx):
        """Print a random cat
        Usage: !cat
        """
        url = "http://random.cat/meow"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                r = await resp.json()
        await self.bot.send_message(ctx.message.channel, r['file'])

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def meme(self, ctx, *args):
        """Generate a meme with 1 or 2 phrases (and with the generator id or without)
        example 1: !meme "Hello there Discord" 47235368
        example 2: !meme "Hello there Discord" "How are you?" 47235368
        """
        print("-------------------------")
        error_count = 0
        generator_id = 0
        phrase1 = ""
        phrase2 = ""
        generator_link = "https://api.imgflip.com/get_memes"
        if len(args) == 1:
            phrase1 = args[0]
            print("Param-1:" + phrase1)
        if len(args) > 1:
            phrase1 = args[0]
            print("Param-2:" + phrase1)
            try:
                generator_id = int(args[1])
                print("GenID:" + str(generator_id))
            except ValueError:
                phrase2 = args[1]
                print("Param2 - not a number")
        if len(args) == 3:
            try:
                generator_id = int(args[2])
                print("GenID:" + str(generator_id))
            except ValueError:
                await self.bot.send_message(ctx.message.channel, "The third param it's not a number!")
                error_count = 1
                print("GenID Not Correct")
        if 3 >= len(args) > 0 == error_count:
            if len(args) < 3 and generator_id == 0:
                async with aiohttp.ClientSession() as session:
                    async with session.get(generator_link) as resp:
                        r = await resp.json()
                generator = r
                if generator['success']:
                    generator_id = generator['data']['memes'][random.randint(0, len(generator['data']['memes']) - 1)][
                        'id']
                else:
                    print("Error getting meme generators")
            request_data = {'template_id': int(generator_id),
                            'username': self.botVariables.get_meme_generator_username(),
                            'password': self.botVariables.get_meme_generator_password(),
                            'text0': phrase1,
                            'text1': phrase2,
                            'boxes[1][text]': phrase1,
                            'boxes[0][text]': phrase2
                            }
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.imgflip.com/caption_image", data=request_data) as resp:
                    r = await resp.text()
                    try:
                        r = await resp.json()
                    except (UnicodeDecodeError, aiohttp.client_exceptions.ClientResponseError):
                        print("Meme reply is not a json...")
                        return
            result = r
            if result['success']:
                await self.bot.send_message(ctx.message.channel,
                                            str(result['data']['url']) + " ID Meme:" + str(generator_id))
            else:
                print("Meme Error:" + str(result['error_message']))
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "meme \"text1\" \"text2 or memeId\"[Optional] \"memeId\"[Optional], for more see " + self.command_prefix + "help meme")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def party(self, ctx):
        """Party Hard Command
        Usage: !party
        """
        print("-------------------------")
        normal_parrot = "https://cdn.discordapp.com/attachments/276674976210485248/304557572416077824/parrot.gif"
        conga_parrot = "https://cdn.discordapp.com/attachments/276667503034499072/309781525971337226/congaparrot.gif"
        shuffle_parrot = "https://cdn.discordapp.com/attachments/276667503034499072/309781549639794688/shuffleparrot.gif"
        link = ""
        number = randint(0, 2)
        print("Number:" + str(number))
        if number == 0:
            link = normal_parrot
        if number == 1:
            link = conga_parrot
        if number == 2:
            link = shuffle_parrot
        try:
            if ctx.message.content == "!party" and ctx.message.server is not None:
                print("Deleting the message...")
                await self.bot.delete_message(ctx.message)
        except (discord.errors.Forbidden, discord.ext.commands.errors.CommandInvokeError):
            print("Can't delete the message(I Need 2FA?)...")
        embed = discord.Embed(title="Party Hard")
        embed.set_author(name=ctx.message.author.name)
        embed.set_thumbnail(url=link)
        await self.bot.send_message(ctx.message.channel, embed=embed)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def printtext(self, ctx, *args):
        """Print a phrase with emotes
        Usage: !printtext "Hello there"
        """
        if len(args) == 1:
            received_string = args[0]
            if received_string.startswith('"') and received_string.endswith('"'):
                received_string = received_string[1:-1]
            pos = received_string.find("\\")
            if pos != -1:
                if received_string[pos + 1] != " ":
                    print("Error:" + received_string[pos + 1])
                    return
            pos = received_string.find("\"")
            if pos != -1:
                print("Error:" + received_string[pos + 1])
                return
            # print(str(stringa))
            final_string = ""
            number_emoji = self.botVariables.numbersEmoji
            for c in received_string:
                # print(c)
                if c.isalnum():
                    try:
                        val = int(c)
                        if val < 10:
                            final_string += number_emoji[val] + " "
                        else:
                            print("fatal Error!!!-" + str(val))

                    except ValueError:
                        c = c.lower()
                        if c == "è" or c == "é" or c == "à" or c == "ù" or c == "ì":
                            final_string += c + " "
                        else:
                            final_string += ":regional_indicator_" + c + ":" + " "
                else:
                    if c == "!" or c == "?" or c == "#":
                        if c == "!":
                            final_string += ":exclamation:" + " "
                        else:
                            if c == "#":
                                final_string += ":hash:" + " "
                            else:
                                final_string += ":question:" + " "
                    else:
                        final_string += c + " "
            await self.bot.send_message(ctx.message.channel, final_string)
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "printtext \"phrase\", for more see " + self.command_prefix + "help printtext")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def quote(self, ctx):
        """Print a random quote
        Usage: !quote
        """
        r = requests.get("http://quotesondesign.com/wp-json/posts?filter[orderby]=rand&filter[posts_per_page]=1")
        await self.bot.send_message(ctx.message.channel, "**" + BotMethods.cleanhtml("From " + r.json()[0]['title'])
                                    + ":**" + html.unescape(BotMethods.cleanhtml(r.json()[0]['content'])))

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def translate(self, ctx, *args):
        """Translate a text
        Usage: !translate "hello there" fr
        """
        if len(args) == 2:
            message_received = str(args[0])
            language = str(args[1])
            try:
                await self.bot.send_message(ctx.message.channel, self.gs.translate(message_received, language))
            except error.HTTPError:
                await self.bot.send_message(ctx.message.channel, "HTTP Error 503: Service Unavailable")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "translate \"message\" language(it/en/de...), for more see " + self.command_prefix + "help translate")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def weather(self, ctx, *args):
        """Print the current weather in a given city
        (0 is now, 1 is 12h later, 2 tomorrow, ...., 19 is the max[12h for 10 days])
        (the country code is in ISO-3166 = 2 letters)
        Usage: !weather Venice
        Usage: !weather IT Rome
        Usage: !weather Rome 1
        Usage: !weather DE Berlino 1
        """
        if len(args) < 1 or len(args) > 3:
            await self.bot.send_message(ctx.message.channel,
                                        "**Please read:** " + self.command_prefix + "help weather")
            return
        else:
            country_code = False
            country_code_str = self.botVariables.get_weather_country()
            city_name = ""
            day = 0
            if len(args) == 1:
                city_name = str(args[0])
            else:  # more than 1 param
                if len(str(args[0])) == 2:  # taking the country code
                    country_code = True
                    country_code_str = str(args[0])
                if len(args) == 2:  # if 2 params
                    if not country_code:  # country code not present
                        city_name = str(args[0])
                        try:
                            day = int(args[1])
                        except ValueError:
                            await self.bot.send_message(ctx.message.channel,
                                                        "**Check the day or the country code, please read:** " + self.command_prefix + "help weather")
                            return
                    else:
                        city_name = str(args[1])
                if len(args) == 3:
                    if not country_code:
                        await self.bot.send_message(ctx.message.channel,
                                                    "**Check the country code, please read:** " + self.command_prefix + "help weather")
                        return
                    else:
                        city_name = str(args[1])
                        try:
                            day = int(args[2])
                        except ValueError:
                            await self.bot.send_message(ctx.message.channel,
                                                        "**Check the day or the country code, please read:** " + self.command_prefix + "help weather")
                            return
            if day > 19:
                await self.bot.send_message(ctx.message.channel,
                                            "**Check the day code, please read:** " + self.command_prefix + "help weather")
                return
            # I've everything now, starting getting the weather
            print("-------------------------")
            print("Making weather request")
            half_day = BotMethods.convert_hours_to_day(
                day)  # this because the weather is divided in 10 days and 20 times 12h
            url = "http://api.wunderground.com/api/" + self.botVariables.get_weather_key() + "/"
            url += "forecast10day/q/" + country_code_str + "/" + city_name + ".json"
            async with aiohttp.ClientSession() as client_session:
                async with client_session.get(url) as response:
                    request_result = await response.json()  # convert the response to a json file
            try:
                await self.bot.send_message(ctx.message.channel, "**Error:** " + str(
                    request_result["response"]["error"][
                        "description"]) + "(check usage with " + self.command_prefix + "help weather)")
                print("Error, weather request failed")
                return
            except KeyError:
                try:  # simple try to see if the key exist
                    str(request_result["forecast"]["txt_forecast"]["forecastday"][day]["title"])
                except KeyError:
                    print("Error - City not defined")
                    final_message = "```\n"
                    final_message += "Error: Multiple Cities found...\n"
                    cont = 0
                    for city in request_result["response"]["results"]:
                        final_message += city["name"] + " - " + city["country_name"] + "(" + city["country"] + ")\n"
                        cont += 1
                        if cont > 4:
                            final_message += "[More...]\n"
                            break
                    final_message += "```"
                    await self.bot.send_message(ctx.message.channel, final_message)
                    return
                print("No errors found in request, creating embed")
                day_name = str(request_result["forecast"]["txt_forecast"]["forecastday"][day]["title"])
                day_number = str(request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["date"]["day"])
                month_number = str(
                    request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["date"]["month"])
                year_number = str(request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["date"]["year"])
                embed = discord.Embed(title="Weather",
                                      colour=discord.Colour(0x088DA5),
                                      url="https://www.wunderground.com/",
                                      description="Weather in \"" + city_name + "\" during \"" + day_name + "\" " + day_number + "/" + month_number + "/" + year_number,
                                      timestamp=datetime.utcfromtimestamp(time.time())
                                      )
                embed.set_thumbnail(url=request_result["forecast"]["txt_forecast"]["forecastday"][day]["icon_url"])
                embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
                try:
                    # description of the day
                    day_description = request_result["forecast"]["txt_forecast"]["forecastday"][day]["fcttext_metric"]
                except KeyError:
                    day_description = "Not found..."
                embed.add_field(name="Short Description:", value=day_description, inline=False)

                try:
                    # min temperature of the day
                    key_value = request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["low"]["celsius"]
                    if key_value == "":
                        temp_min = "Not available"
                    else:
                        temp_min = key_value
                except KeyError:
                    temp_min = "Not found..."
                embed.add_field(name="Min Temperature:", value=temp_min, inline=True)

                try:
                    # max temperature of the day
                    key_value = request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["high"]["celsius"]
                    if key_value == "":
                        temp_max = "Not available"
                    else:
                        temp_max = key_value
                except KeyError:
                    temp_max = "Not found..."
                embed.add_field(name="Max Temperature:", value=temp_max, inline=True)

                try:
                    # Average Humidity temperature of the day
                    avg_humid = str(
                        request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["avehumidity"]) + "%"
                except KeyError:
                    avg_humid = "Not found..."
                embed.add_field(name="Average Humidity:", value=avg_humid, inline=True)

                try:
                    # short weather condition
                    condition = request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["conditions"]
                except KeyError:
                    condition = "Not found..."
                embed.add_field(name="Conditions:", value=condition, inline=True)

                embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())
                try:
                    await self.bot.send_message(ctx.message.channel, embed=embed)
                except HTTPException:
                    await self.bot.send_message(ctx.message.channel,
                                                "*A strange error occurred, cannot retrieve that city, sorry...*")
            print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def lmgtfy(self, ctx, *args):
        """Generate a "let me google it for you" url
        Usage: !lmgtfy "search box"
        Example: !lmgtfy "helllo world"
        """
        print("-------------------------")
        if len(args) == 1:
            try:
                if ctx.message.server is not None:
                    print("Deleting the message...")
                    await self.bot.delete_message(ctx.message)
            except discord.errors.Forbidden:
                print("Can't delete the message...")
            # get the api ket and generate the url
            api_key = self.botVariables.get_google_shortener_key()
            search_term = urllib.parse.quote(args[0])
            url = "http://lmgtfy.com/?q=" + search_term
            # prepare the request
            post_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(api_key)
            payload = {'longUrl': url}
            headers = {'content-type': 'application/json'}
            # make post request
            async with aiohttp.ClientSession() as session:
                async with session.post(post_url, data=json.dumps(payload),
                                        headers=headers) as resp:  # the website use get
                    r = await resp.json()
            await self.bot.send_message(ctx.message.channel, "**Your Url:** " + r["id"] +
                                        "\n (Generated by: " + ctx.message.author.mention + ")")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "lmgtfy \"search box\", for more see " + self.command_prefix + "help lmgtfy")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def hacked(self, ctx, *args):
        """Check if the email or the username have been hacked
        Usage: !hacked test@test.it
        """
        print("-------------------------")
        if len(args) == 1:
            try:
                if ctx.message.server is not None:
                    print("Deleting the message...")
                    await self.bot.delete_message(ctx.message)
            except discord.errors.Forbidden:
                print("Can't delete the message...")
            url = "https://haveibeenpwned.com/api/v2/breachedaccount/"
            print("Request:" + url + "Email")
            r_json = None  # declare the json
            async with aiohttp.ClientSession() as session:
                async with session.get(url + str(args[0])) as resp:  # the website use get
                    r = await resp.text()
                    try:
                        r_json = await resp.json()
                    except (UnicodeDecodeError, aiohttp.client_exceptions.ClientResponseError):
                        print("Hacked reply is not a json...")
            if str(r) == "<Response [404]>" or str(r) == "":
                print("Not found")
                embed = discord.Embed(title="Hacked?", url='https://haveibeenpwned.com/', color=0x2fea00)
                embed.set_author(name="Analysis required by " + ctx.message.author.name,
                                 icon_url=ctx.message.author.avatar_url)
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/276674976210485248/304961315326394369/1492796826_Tick_Mark_Dark.png')
                embed.add_field(name="Result:", value="Everything is ok! No problems found", inline=False)
                embed.set_footer(text="Using haveibeenpwned.com")
                await self.bot.send_message(ctx.message.channel, embed=embed)
            else:
                json_received = r_json
                print(len(json_received))
                embed = discord.Embed(title="Hacked?", url='https://haveibeenpwned.com/',
                                      description="Websites where you are registered that have been hacked:",
                                      color=0xff0000)
                embed.set_author(name="Analysis required by " + ctx.message.author.name,
                                 icon_url=ctx.message.author.avatar_url)
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/276674976210485248/304963039545786368/1492797249_shield-error.png')
                for index in range(len(json_received)):
                    value_to_print = "**Website:** " + str(json_received[index]['Domain']) + "\n**Date:** " + str(
                        json_received[index]['BreachDate'])
                    value_to_print += "\n**Stolen:** "
                    for currentIndex in range(len(json_received[index]['DataClasses'])):
                        value_to_print += str(json_received[index]['DataClasses'][currentIndex]) + ", "
                    embed.add_field(name=str(json_received[index]['Title']), value=value_to_print, inline=False)
                embed.set_footer(text="Using haveibeenpwned.com")
                await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "hacked \"email or username\", for more see " + self.command_prefix + "help hacked")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def ur(self, ctx, *args):
        """Search a word in the urban dictionary
        Usage: !ur <WORD>
        Example: !ur dunno
        """
        print("-------------------------")
        if len(args) == 1:
            request_link = "http://api.urbandictionary.com/v0/define?term=" + str(args[0])
            # request_result = requests.get(request_link).json()
            async with aiohttp.ClientSession() as session:
                async with session.get(request_link) as resp:  # the website use get
                    request_result = await resp.json()
            if request_result["result_type"] == "no_results":  # no results found
                print("No results for that word in urban dictionary")
                await self.bot.send_message(ctx.message.channel,
                                            "*No results found for \"" + str(args[0]) + "\" in urban dictionary*")
            else:
                current_max_vote = float(0.0)
                saved_definition = None
                if request_result["result_type"] == "exact":  # found an exact result
                    for definition in request_result["list"]:  # choose the best result with positive-percentage
                        percentage = (definition["thumbs_up"] / (
                                definition["thumbs_up"] + definition["thumbs_down"])) * 100
                        if percentage > current_max_vote:
                            saved_definition = definition
                            current_max_vote = percentage
                    # create the embed to send
                    embed = discord.Embed(title="Urban Dictionary - Link", url=saved_definition["permalink"],
                                          color=0x1d2439,
                                          description="Best dictionary result for \"" + str(args[0]) + "\"")
                    embed.set_author(name="Search required by " + ctx.message.author.name,
                                     icon_url=ctx.message.author.avatar_url)
                    embed.set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/276674976210485248/350641481872179200/featured-image4.jpg')
                    definition_text = saved_definition["definition"]
                    if len(definition_text) > 1024:  # cut the string, is too long
                        definition_text = definition_text[:1000] + "[TEXT TOO LONG]..."
                    embed.add_field(name="Definition:", value=definition_text, inline=False)
                    example_text = saved_definition["example"]
                    if len(example_text) > 1024:  # cut the string, is too long
                        example_text = example_text[:1000] + "[TEXT TOO LONG]..."
                    embed.add_field(name="Example(s):", value=example_text, inline=False)
                    embed.add_field(name="Author:", value=saved_definition["author"], inline=True)
                    embed.add_field(name="Positive Votes:", value=str(int(current_max_vote)) + "%", inline=True)
                    embed.set_footer(text="Using http://www.urbandictionary.com/")
                    try:
                        await self.bot.send_message(ctx.message.channel, embed=embed)
                        print("Ur embed sent successfully")
                    except discord.errors.HTTPException:
                        print("HTTPException during the sending of ur embed")
                        await self.bot.send_message(ctx.message.channel, "*An error occurred sending the result...*")
                else:
                    print("Urban Dictionary request fail")
                    await self.bot.send_message(ctx.message.channel, "*Urban-Dictionary search failed*")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "ur word, for more see " + self.command_prefix + "help ur")
        print("-------------------------")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotCommonCommands(bot))
