# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import html
import re
import json
import random
import discord
import goslate
import time
import urllib.parse
import aiohttp

from discord.errors import HTTPException
from urllib import error
from datetime import datetime
from botMethodsClass import BotMethods


# ---------------------------------------------------------------------


class BotCommonCommands(commands.Cog):
    """ Class with Bot 'Common' commands (simple commands, for example cat, meme or gif) """
    # ---------------------------------------------------------------------

    # list of class essential variables, the None variables are assigned in the constructor because i need the bot reference
    botVariables = None  # used to get api keys and other bot informations
    gs = goslate.Goslate()  # translator (used in translate command)
    command_prefix = None  # bot command prefix

    async def get_short_url(self, url):
        """
        This function use the google api to generate a shorter version of the url given
        :param url: the url to make shorten
        :return: a short version of the url
        """
        api_key = self.botVariables.get_rebrandly_shortener_key()

        link_request = {
            "destination": url
        }

        request_headers = {
            "Content-type": "application/json",
            "apikey": api_key
        }
        # make post request
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.rebrandly.com/v1/links", data=json.dumps(link_request),
                                    headers=request_headers) as resp:  # the website use get
                r = await resp.json()
        if "shortUrl" in r:
            return "https://" + r["shortUrl"]
        else:
            print("Error in get_short_url")
            return "Error " + str(r)

    # ---------------------------------------------------------------------

    @commands.command()
    async def gif(self, ctx: discord.ext.commands.Context, *args):
        """Return a random gif (with 0 or more params)
        Usage: !gif x1 x2 x3[Optional]
        Example: !gif or !gif funny cat
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        currentgifkey = self.botVariables.get_gif_key()
        print("GifRequest:Arguments:" + str(len(args)))
        tag = ""
        if len(args) == 0:  # request a random gif
            print("Gif Request with No arguments")
            url = "http://api.giphy.com/v1/gifs/random?api_key=" + currentgifkey
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    r = await resp.json()
            if 'data' in r:
                await message_channel.send(r['data']['image_url'])
            elif 'message' in r:
                await message_channel.send("An error occurred:" + r['message'])
        else:  # request a gif with tags
            for x in range(0, len(args)):
                tag = tag + args[x]
                if x != (len(args) - 1):
                    tag += " "
            tag = urllib.parse.quote(tag)
            url = "http://api.giphy.com/v1/gifs/random?api_key=" + currentgifkey + "&tag=" + tag
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    r = await resp.json()
            print("GifRequest:Gif Found")
            if (len(r['data'])) == 0:
                await message_channel.send("No GIF found with those tags :frowning: ")
            else:
                if 'data' in r:
                    await message_channel.send(r['data']['image_url'])
                elif 'message' in r:
                    await message_channel.send("An error occurred:" + r['message'])
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def cat(self, ctx: discord.ext.commands.Context):
        """Print a random cat
        Usage: !cat
        """
        url = "http://aws.random.cat/meow"
        message_channel: discord.abc.Messageable = ctx.message.channel
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    r = await resp.json()
            await message_channel.send(r['file'])
        except aiohttp.ContentTypeError:
            print("Cannot send cat image...")

    # ---------------------------------------------------------------------

    @commands.command()
    async def meme(self, ctx: discord.ext.commands.Context, *args):
        """Generate a meme with up to 3 phrases (and with the generator id or without)
        example 1: !meme "Hello there Discord" 47235368
        example 2: !meme "Generate a random meme" "For me"
        example 3: !meme "Hello there Discord" "How are you?" 47235368
        example 4: !meme "Hello there Discord" "How are you?" "I'm ok" 47235368
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        error_flag = False
        generator_id = 0
        phrase1 = None
        phrase2 = None
        phrase3 = None
        generator_link = "https://api.imgflip.com/get_memes"
        if len(args) == 1:  # there is only one parameter for the meme
            phrase1 = args[0]
        if len(args) > 1:  # more than one parameter for the meme
            phrase1 = args[0]
            try:  # is the second parameter a number?
                generator_id = int(args[1])
                print("Meme: GenID:" + str(generator_id))
            except ValueError:  # no, use it as string
                phrase2 = args[1]
                print("Meme: Param2 - not the generator ID")
        if len(args) == 3:
            try:
                generator_id = int(args[2])  # is the third parameter the generator id?
                print("Meme: GenID:" + str(generator_id))
            except ValueError:
                print("Meme: Param3 - not the generator ID")
                phrase3 = args[2]  # if no use it as third string
        else:
            if len(args) == 4:
                phrase3 = args[2]  # the third parameter is used as string
                try:
                    generator_id = int(args[3])  # check is the generator id is valid
                    print("Meme: GenID:" + str(generator_id))
                except ValueError:
                    await message_channel.send("The fourth param it's not a number!")
                    error_flag = True
                    print("Meme: GenID Not Correct")
        if 0 < len(args) <= 4 and not error_flag:  # check for parameters and errors
            if generator_id == 0:  # generator id not given, downloading a random id
                async with aiohttp.ClientSession() as session:
                    async with session.get(generator_link) as resp:
                        r = await resp.json()
                generator = r
                if generator['success']:
                    generator_id = generator['data']['memes'][random.randint(0, len(generator['data']['memes']) - 1)][
                        'id']
                else:
                    print("Error getting meme generators")
            if phrase2 is None:  # request data based for only 1 text box
                print("Meme: Generating meme with 1 boxes")
                request_data = {'template_id': int(generator_id),
                                'username': self.botVariables.get_meme_generator_username(),
                                'password': self.botVariables.get_meme_generator_password(),
                                'text0': phrase1,
                                'boxes[0][text]': phrase1
                                }
            else:
                if phrase3 is None:  # request data based if we have 3 or 2 boxes
                    print("Meme: Generating meme with 2 boxes")
                    request_data = {'template_id': int(generator_id),
                                    'username': self.botVariables.get_meme_generator_username(),
                                    'password': self.botVariables.get_meme_generator_password(),
                                    'text0': phrase1,
                                    'text1': phrase2,
                                    'boxes[0][text]': phrase1,
                                    'boxes[1][text]': phrase2
                                    }
                else:
                    print("Meme: Generating meme with 3 boxes")
                    request_data = {'template_id': int(generator_id),
                                    'username': self.botVariables.get_meme_generator_username(),
                                    'password': self.botVariables.get_meme_generator_password(),
                                    'text0': phrase1,
                                    'text1': phrase2,
                                    'boxes[0][text]': phrase1,
                                    'boxes[1][text]': phrase2,
                                    'boxes[2][text]': phrase3
                                    }
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.imgflip.com/caption_image", data=request_data) as resp:
                    try:
                        r = await resp.json()
                    except (UnicodeDecodeError, aiohttp.ClientResponseError):
                        print("Meme reply is not a json...")
                        await message_channel.send("*An error occurred generating the meme...*")
                        return
            result = r
            if result['success']:
                await message_channel.send(str(result['data']['url']) + " ID Meme:" + str(generator_id))
            else:
                print("Meme Error:" + str(result['error_message']))
                await message_channel.send("*An error occurred generating the meme...*")
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "meme <parameters>, please check " + self.command_prefix + "help meme")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def party(self, ctx: discord.ext.commands.Context):
        """Party Hard Command
        Usage: !party
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        parrots = ["https://cdn.discordapp.com/attachments/276674976210485248/304557572416077824/parrot.gif",
                   "https://cdn.discordapp.com/attachments/276667503034499072/309781525971337226/congaparrot.gif",
                   "https://cdn.discordapp.com/attachments/276667503034499072/309781549639794688/shuffleparrot.gif"]
        link = random.choice(parrots)
        try:
            if ctx.message.content == "!party" and ctx.message.guild is not None:
                print("Deleting the message...")
                await ctx.message.delete()
        except (discord.errors.Forbidden, discord.ext.commands.errors.CommandInvokeError):
            print("Can't delete the message(I Need 2FA?)...")
        embed = discord.Embed(title="Party Hard")
        embed.set_author(name=ctx.message.author.name)
        embed.set_thumbnail(url=link)
        await message_channel.send(embed=embed)
        print("Parrot sent!")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def printtext(self, ctx: discord.ext.commands.Context, *args):
        """Print a phrase with emotes
        Usage: !printtext "Hello there"
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) == 1:
            received_string = args[0]
            if received_string.startswith('"') and received_string.endswith('"'):
                received_string = received_string[1:-1]
            pos = received_string.find("\\")
            if pos != -1 and received_string[pos + 1] != " ":
                print("Error:" + received_string[pos + 1])
                return
            pos = received_string.find("\"")
            if pos != -1:
                print("Error:" + received_string[pos + 1])
                return
            final_string = ""
            number_emoji = self.botVariables.numbers_emoji
            for c in received_string:
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
            await message_channel.send(final_string)
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "printtext \"phrase\", for more see " + self.command_prefix + "help printtext")

    # ---------------------------------------------------------------------

    @commands.command()
    async def quote(self, ctx: discord.ext.commands.Context):
        """Print a random quote
        Usage: !quote
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "http://quotesondesign.com/wp-json/posts?filter[orderby]=rand&filter[posts_per_page]=1") as resp:
                r = await resp.json()
        await message_channel.send("**" + BotMethods.cleanhtml("From " + r[0]['title']) + ":**" + html.unescape(
            BotMethods.cleanhtml(r[0]['content'])))

    # ---------------------------------------------------------------------

    @commands.command()
    async def translate(self, ctx: discord.ext.commands.Context, *args):
        """Translate a text
        Usage: !translate "hello there" fr
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) == 2:
            message_received = str(args[0])
            language = str(args[1])
            try:
                await message_channel.send("**Translated text:**" + self.gs.translate(message_received, language))
            except error.HTTPError:
                await message_channel.send("HTTP Error 503: Service Unavailable")
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "translate \"message\" language(it/en/de...), for more see " + self.command_prefix + "help translate")

    # ---------------------------------------------------------------------

    @commands.command()
    async def weather(self, ctx: discord.ext.commands.Context, *args):
        """Print the current weather in a given city
        It can be asked for 1 to 5 days, 1 is default
        (the country code is in ISO-3166 = 2 letters)
        Usage: !weather Venice
        Usage: !weather IT Rome
        Usage: !weather Rome 1
        Usage: !weather DE Berlino 1
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) < 1 or len(args) > 3:
            await message_channel.send("**Please read:** " + self.command_prefix + "help weather")
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
                            await message_channel.send(
                                "**Check the day or the country code, please read:** " + self.command_prefix + "help weather")
                            return
                    else:
                        city_name = str(args[1])
                if len(args) == 3:
                    if not country_code:
                        await message_channel.send(
                            "**Check the country code, please read:** " + self.command_prefix + "help weather")
                        return
                    else:
                        city_name = str(args[1])
                        try:
                            day = int(args[2])
                        except ValueError:
                            await message_channel.send(
                                "**Check the day or the country code, please read:** " + self.command_prefix + "help weather")
                            return
            if day > 5:
                await message_channel.send(
                    "**Check the day code, please read:** " + self.command_prefix + "help weather")
                return
            # Find the city id
            weather_api_key = self.botVariables.get_weather_key()
            weather_api_language = self.botVariables.get_weather_language()
            print("Making city request")
            city_url = "http://dataservice.accuweather.com/locations/v1/cities/" + country_code_str + "/search?apikey="
            city_url += str(weather_api_key)
            city_url += "&q=" + urllib.parse.quote_plus(str(city_name))
            city_url += "&language=" + weather_api_language
            async with aiohttp.ClientSession() as client_session:
                async with client_session.get(city_url) as response:
                    city_request_result = await response.json()
            if city_request_result == "":
                await message_channel.send("*Can't find a valid city with that name...*")
                return
            if len(city_request_result) == 0:
                await message_channel.send(
                    "*Can't find a valid city with that name, check that the country code is valid "
                    "and remember that the city name must be in language:" +
                    weather_api_language + "...*")
                return
            city_id = city_request_result[0]['Key']
            # I've everything now, starting getting the weather
            print("-------------------------")
            print("Making weather request")
            url = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + str(city_id)
            url += "?apikey=" + weather_api_key
            url += "&language=" + weather_api_language
            url += "&details=true&metric=true"
            async with aiohttp.ClientSession() as client_session:
                async with client_session.get(url) as response:
                    request_result = await response.json()  # convert the response to a json file
            try:
                await message_channel.send("**Error:** Code:" + str(request_result["Code"]) + " Message" + str(
                    request_result["Message"]) + "(check usage with " + self.command_prefix + "help weather)")
                print("Error, weather request failed - " + str(request_result))
                return
            except KeyError:
                try:  # simple try to see if the key exist
                    str(request_result["DailyForecasts"][0]["Date"])
                except KeyError:
                    print("Error - Can't read the response from server")
                    await message_channel.send("Error - Can't read the response from server")
                    return
                print("No errors found in request, creating embed")
                description = "Weather in " + city_name + " ["
                description += city_request_result[0]['AdministrativeArea']['LocalizedName'] + "] ["
                description += city_request_result[0]['Country']['LocalizedName'] + "]"
                embed = discord.Embed(title="AccuWeather Weather",
                                      colour=discord.Colour(0x088DA5),
                                      url=request_result['Headline']['Link'],
                                      description=description,
                                      timestamp=datetime.utcfromtimestamp(time.time())
                                      )
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/396666575081439243/575372381162569728/86e3c061daf1a86ed17d74eb0948f713.png")
                embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
                try:
                    # description of the day
                    day_description = request_result["Headline"]["Text"]
                except KeyError:
                    day_description = "Not found..."
                embed.add_field(name="Short Description:", value=day_description, inline=False)

                for i in range(0, max(1, day)):
                    day_element = request_result['DailyForecasts'][i]
                    date_time_str = day_element['Date'][:10]
                    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d')
                    title = "Weather in " + str(date_time_obj.day) + "/" + str(date_time_obj.month) + "/" + str(
                        date_time_obj.year)
                    content = "Temperature Min:" + str(day_element['Temperature']['Minimum']['Value']) + str(
                        day_element['Temperature']['Minimum']['Unit'])
                    content += " - Max:" + str(day_element['Temperature']['Maximum']['Value']) + str(
                        day_element['Temperature']['Maximum']['Unit'])
                    content += " - Weather during day:" + str(day_element['Day']['ShortPhrase'])
                    content += " - Weather during night:" + str(day_element['Night']['ShortPhrase'])

                    embed.add_field(name=title, value=content, inline=False)

                embed.set_footer(text=self.botVariables.get_description(), icon_url=self.botVariables.get_bot_icon())
                try:
                    await message_channel.send(embed=embed)
                except HTTPException:
                    await message_channel.send("*A strange error occurred, cannot retrieve that city, sorry...*")
            print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def short(self, ctx: discord.ext.commands.Context, *args):
        """Generate a short url from the url given as parameter
        Usage: !short https://www.yoururl.blabla
        Example: !short https://www.google.it/imghp
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) == 1:
            try:
                if ctx.message.guild is not None:
                    print("Deleting the message...")
                    await ctx.message.delete()
            except discord.errors.Forbidden:
                print("Can't delete the message...")
            async with message_channel.typing():
                short_url = await self.get_short_url(args[0])
                if short_url.startswith("Error"):  # An error occurred
                    await message_channel.send("**An error occurred** " + short_url)
                else:
                    await message_channel.send(
                        "**Your Short Url:** " + short_url + "\n (Generated by: " + ctx.message.author.mention + ")")
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "short <longurl>, for more see " + self.command_prefix + "help short")

    # ---------------------------------------------------------------------

    @commands.command(hidden=True)
    async def showcolor(self, ctx: discord.ext.commands.Context, *args):
        """Show an image with the given color code
        Usage: !showcolor #COLORHEX/(R,G,B)
        Example: !showcolor #ff0000
        Example: !showcolor (255, 0, 0)
        """
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) == 1:
            argstring = str(args[0]).strip()
            # request the color informations to the api
            if argstring.startswith("(") and argstring.endswith(")"):
                url = "http://www.thecolorapi.com/id?rgb=rgb("
                rgblist = argstring[1:-1].split(',')
                for color in rgblist:
                    url += color.strip() + ","
                url = url[:-1] + ")"
            elif argstring.startswith("#"):
                url = "http://www.thecolorapi.com/id?hex=" + argstring[1:]
            else:
                await message_channel.send(
                    "Color format non valid, for more see " + self.command_prefix + "help showcolor")
                return
            reply_error = False
            request_result = None
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:  # the website use get
                    if not str(resp.status) == "200":
                        reply_error = True
                    else:
                        request_result = await resp.json()
            if reply_error:
                await message_channel.send("*An error occurred requesting the color... is your color code valid?*")
            else:
                embed = discord.Embed(title="Color Display", url=request_result["image"]["bare"],
                                      color=(request_result["rgb"]["r"] << 16) + (request_result["rgb"]["g"] << 8) +
                                            request_result["rgb"]["b"])
                embed.set_author(name="Color asked by by " + ctx.message.author.name,
                                 icon_url=ctx.message.author.avatar_url)
                embed.add_field(name="Color Hex Value:", value=request_result["hex"]["value"], inline=False)
                embed.add_field(name="Color RGB Value:", value=request_result["rgb"]["value"], inline=False)
                embed.set_footer(text=self.botVariables.get_description(),
                                 icon_url=self.botVariables.get_bot_icon())
                await message_channel.send(embed=embed)
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "showcolor #COLORHEX/\"(R,G,B)\", for more see " + self.command_prefix + "help showcolor")

    # ---------------------------------------------------------------------

    @commands.command()
    async def lmgtfy(self, ctx: discord.ext.commands.Context, *args):
        """Generate a "let me google it for you" url
        Usage: !lmgtfy "search box"
        Example: !lmgtfy "hello world"
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) == 1:
            try:
                if ctx.message.guild is not None:
                    print("Deleting the message...")
                    await ctx.message.delete()
            except discord.errors.Forbidden:
                print("Can't delete the message...")
            # get the api ket and generate the url
            url = "http://lmgtfy.com/?q=" + urllib.parse.quote(args[0])
            # prepare the request
            short_url = await self.get_short_url(url)
            await message_channel.send(
                "**Your Url:** " + short_url + "\n (Generated by: " + ctx.message.author.mention + ")")
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "lmgtfy \"search box\", for more see " + self.command_prefix + "help lmgtfy")

    # ---------------------------------------------------------------------

    @commands.command()
    async def hacked(self, ctx: discord.ext.commands.Context, *args):
        """Check if the email or the username have been hacked
        Usage: !hacked test@test.it
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) == 1:
            try:
                if ctx.message.guild is not None:
                    print("Deleting the message...")
                    await ctx.message.delete()
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
                    except (UnicodeDecodeError, aiohttp.ClientResponseError):
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
                await message_channel.send(embed=embed)
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
                    for current_index in range(len(json_received[index]['DataClasses'])):
                        value_to_print += str(json_received[index]['DataClasses'][current_index]) + ", "
                    embed.add_field(name=str(json_received[index]['Title']), value=value_to_print, inline=False)
                embed.set_footer(text="Using haveibeenpwned.com")
                await message_channel.send(embed=embed)
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "hacked \"email or username\", for more see " + self.command_prefix + "help hacked")
        print("-------------------------")

    # ---------------------------------------------------------------------

    # Little class used to store definitions in an array
    class UrbanDefinition(object):
        author = ""
        example = ""
        definition = ""
        votes = 0

        def __init__(self, author: str, example: str, definition: str, votes: float):
            self.author = author
            self.example = example
            self.definition = definition
            self.votes = votes

    @commands.command()
    async def ur(self, ctx: discord.ext.commands.Context, *args):
        """Search a word in the urban dictionary
        Usage: !ur <WORD>
        Usage: !ur <WORD> <NumberOfResults(default = 1)>
        Example: !ur dunno
        Example: !ur dunno 5
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) == 1 or len(args) == 2:
            request_link = "http://api.urbandictionary.com/v0/define?term=" + str(args[0])
            async with aiohttp.ClientSession() as session:
                async with session.get(request_link) as resp:  # the website use get
                    request_result = await resp.json()
            if len(request_result["list"]) == 0:  # no results found
                print("No results for that word in urban dictionary")
                await message_channel.send("*No results found for \"" + str(
                    args[0]) + "\" in urban dictionary*")
            else:
                # Store all definitions in an array
                definitions_found = []
                for definition in request_result["list"]:  # choose the best result with positive-percentage
                    div = definition["thumbs_up"] + definition["thumbs_down"]
                    if div == 0:
                        percentage = 0
                    else:
                        percentage = (definition["thumbs_up"] / (div)) * 100
                        percentage = percentage * (definition["thumbs_up"] + definition["thumbs_down"])
                    definitions_found.append(
                        self.UrbanDefinition(definition['author'], definition['example'], definition['definition'],
                                             percentage)
                    )
                # Sort the definition using votes
                definitions_found.sort(key=lambda UrbanDefinition: UrbanDefinition.votes, reverse=True)
                # create the embed to send
                if len(args) == 2 and args[1].isdigit():
                    number_of_results = int(args[1])
                else:
                    number_of_results = 1
                embed = discord.Embed(title="Urban Dictionary - Link",
                                      url="https://www.urbandictionary.com/define.php?term=" +
                                          urllib.parse.quote(str(args[0])),
                                      color=0x1d2439,
                                      description="Best " + str(
                                          number_of_results) + " urban dictionary results for \"" + str(args[0]) + "\"")
                embed.set_author(name="Search required by " + ctx.message.author.name,
                                 icon_url=ctx.message.author.avatar_url)
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/276674976210485248/350641481872179200/featured-image4.jpg')
                # Calculate number of results to display and start creating the embed fields
                for x in range(0, min(len(definitions_found), number_of_results)):
                    # Check text and prepare embed
                    definition_text = definitions_found[x].definition
                    if len(definition_text) > 1024:  # cut the string, is too long
                        definition_text = definition_text[:1000] + "[TEXT TOO LONG]..."
                    embed.add_field(name=("Definition (From " + str(definitions_found[x].author) + "):"),
                                    value=definition_text, inline=False)
                    example_text = definitions_found[x].example
                    if len(example_text) > 1024:  # cut the string, is too long
                        example_text = example_text[:1000] + "[TEXT TOO LONG]..."
                    elif len(example_text) < 5:
                        example_text = "Example not available..."
                    embed.add_field(name="Example(s):", value=example_text, inline=False)
                    embed.add_field(name="---------------------------------------------",
                                    value="---------------------------------------------", inline=False)
                # End for, add footer and send the embed
                embed.set_footer(text="Using http://www.urbandictionary.com/")
                try:
                    await message_channel.send(embed=embed)
                    print("Ur embed sent successfully")
                except discord.errors.HTTPException:
                    print("HTTPException during the sending of ur embed")
                    await message_channel.send("*An error occurred sending the result...*")
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "ur word, for more see " + self.command_prefix + "help ur")
        print("-------------------------")

    # ---------------------------------------------------------------------

    # Little class used to store films in array
    class FilmInfo(object):
        film_id = ""
        film_name = ""
        similar = 0

        def __init__(self, filmid: str, filmname: str, similar: float):
            self.film_id = filmid
            self.film_name = filmname
            self.similar = similar

    @commands.command()
    async def movievotes(self, ctx: discord.ext.commands.Context, *args):
        """Search the movie votes in metacritic database
        Usage: !movievotes <film Title>
        Example: !movievotes "Avengers: Infinity War"
        """
        print("-------------------------")
        message_channel: discord.abc.Messageable = ctx.message.channel
        if len(args) == 1:
            print("Starting search")
            api_key = self.botVariables.get_mashape_metacritic_key()
            search_term = (re.sub(r'([^\s\w]|_)+', '', args[0])).lower()
            request_search_link = "https://api-marcalencc-metacritic-v1.p.mashape.com/search/" + str(
                urllib.parse.quote(search_term)) + "/movie?limit=20&offset=1"
            # search all the films with the term given
            async with aiohttp.ClientSession() as session:
                # the website use get
                async with session.get(request_search_link, headers={'X-Mashape-Key': str(api_key),
                                                                     'Accept': 'application/json'}) as resp:
                    request_result = await resp.json()
            if len(request_result[0]['SearchItems']) > 0:  # there is at least one film
                films_found = []
                max_prob = 0.0
                # decide the best film using string similarity
                for entry in request_result[0]['SearchItems']:
                    entry_string = (re.sub(r'([^\s\w]|_)+', '', entry['Title'])).lower()
                    film_similarity = BotMethods.similar(search_term, entry_string, None)
                    if film_similarity > 0.7:  # consider it only if it's > 0.7 (range is 0.0-1.0)
                        films_found.append(
                            self.FilmInfo(entry['Id'], entry['Title'], film_similarity))  # store that film in the array
                        if film_similarity > max_prob:  # search for max prob
                            max_prob = film_similarity
                            if film_similarity >= 1.0:  # i have found the perfect string
                                print("Perfect name found, search cycle stopped")
                                break  # stop the for
                if len(films_found) > 0:  # i have found at least one possible film
                    film_web_id = ""
                    for film in films_found:  # search the film with the max name similarity in the array
                        if film.similar == max_prob:
                            print("Film Chosen: " + film.film_name + " - Film web id:" + str(
                                film.film_id) + " - Sim.:" + str(
                                max_prob))
                            film_web_id = film.film_id  # get the film web id
                            break
                    # make request to get all necessary film informations
                    request_search_link = "https://api-marcalencc-metacritic-v1.p.mashape.com" + str(film_web_id)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(request_search_link, headers={'X-Mashape-Key': str(api_key),
                                                                             'Accept': 'application/json'}) as resp:  # the website use get
                            request_result = await resp.json()
                    if 'message' in request_result:
                        await message_channel.send("*An error occurred downloading the data...*")
                        return
                    # prepare the embed message
                    embed = discord.Embed(title=str(request_result[0]['Title']),
                                          colour=discord.Colour(0xffcc00),
                                          url="http://www.metacritic.com" + str(film_web_id),
                                          description="Metacritic votes about " + str(
                                              request_result[0]['Title']) + " by " + str(
                                              request_result[0]['Director']) + ", released on " + str(
                                              request_result[0]['ReleaseDate']),
                                          timestamp=datetime.utcfromtimestamp(time.time())
                                          )
                    if 'ImageUrl' in request_result[0]:
                        embed.set_thumbnail(url=str(request_result[0]['ImageUrl']))
                    else:
                        print("No ImageUrl found, no thumbnail set")
                    embed.set_author(name=ctx.message.author.name, url="", icon_url=ctx.message.author.avatar_url)
                    embed.set_footer(text=self.botVariables.get_description(),
                                     icon_url=self.botVariables.get_bot_icon())
                    if len(request_result[0]['Rating']) > 0:
                        # --- read users votes ---
                        user_votes = "Rating: " + str(request_result[0]['Rating']['UserRating']) + " (" + str(
                            request_result[0]['Rating']['UserReviewCount']) + " votes)"
                        # --- read critic votes ---
                        critic_votes = "Rating: " + str(request_result[0]['Rating']['CriticRating']) + " (" + str(
                            request_result[0]['Rating']['CriticReviewCount']) + " votes)"
                        # --- create fields ---
                        embed.add_field(name="Critic Rating", value=critic_votes)
                        embed.add_field(name="User Rating", value=user_votes)
                    else:
                        embed.add_field(name="No votes found...",
                                        value="Looks like there are no votes for this film...")
                    # --- sending the message ---
                    print("Sending film embed message")
                    await message_channel.send(embed=embed)
                else:
                    print("No films found")
                    await message_channel.send("*No films found, check the name...*")
            else:
                print("No films found")
                await message_channel.send("*No films found, check the name...*")
        else:
            await message_channel.send(
                "**Usage:** " + self.command_prefix + "movievotes <film Title>, for more see " + self.command_prefix + "help movievotes")
        print("-------------------------")

    # ---------------------------------------------------------------------

    def __init__(self, bot: discord.ext.commands.Bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot
        self.botVariables = self.bot.bot_variables_reference
        # assigning variables value now i can use botVariables
        self.command_prefix = self.botVariables.command_prefix

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotCommonCommands(bot))
