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


class BotCommonCommands:
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
        api_key = self.botVariables.get_google_shortener_key()
        post_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(api_key)
        payload = {'longUrl': url}
        headers = {'content-type': 'application/json'}
        # make post request
        async with aiohttp.ClientSession() as session:
            async with session.post(post_url, data=json.dumps(payload),
                                    headers=headers) as resp:  # the website use get
                r = await resp.json()
        if "id" in r:
            return r["id"]
        else:
            print("Error in get_short_url")
            error_string = "Error " + str(r["error"]["code"]) + "(" + r["error"]["message"] + ")"
            if len(r["error"]["errors"]) > 0:  # Contains a list of errors
                error_string += " - "
                for err in r["error"]["errors"]:  # Print all errors
                    error_string += err["message"] + " "
            return error_string

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
        if len(args) == 0:  # request a random gif
            print("Gif Request with No arguments")
            url = "http://api.giphy.com/v1/gifs/random?api_key=" + currentgifkey
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    r = await resp.json()
            await self.bot.send_message(ctx.message.channel, r['data']['image_url'])
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
        url = "http://aws.random.cat/meow"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    r = await resp.json()
            await self.bot.send_message(ctx.message.channel, r['file'])
        except aiohttp.ContentTypeError:
            print("Cannot send cat image...")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def meme(self, ctx, *args):
        """Generate a meme with up to 3 phrases (and with the generator id or without)
        example 1: !meme "Hello there Discord" 47235368
        example 2: !meme "Generate a random meme" "For me"
        example 3: !meme "Hello there Discord" "How are you?" 47235368
        example 4: !meme "Hello there Discord" "How are you?" "I'm ok" 47235368
        """
        print("-------------------------")
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
                    await self.bot.send_message(ctx.message.channel, "The fourth param it's not a number!")
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
                        await self.bot.send_message(ctx.message.channel, "*An error occurred generating the meme...*")
                        return
            result = r
            if result['success']:
                await self.bot.send_message(ctx.message.channel,
                                            str(result['data']['url']) + " ID Meme:" + str(generator_id))
            else:
                print("Meme Error:" + str(result['error_message']))
                await self.bot.send_message(ctx.message.channel, "*An error occurred generating the meme...*")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "meme <parameters>, please check " + self.command_prefix + "help meme")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def party(self, ctx):
        """Party Hard Command
        Usage: !party
        """
        print("-------------------------")
        parrots = ["https://cdn.discordapp.com/attachments/276674976210485248/304557572416077824/parrot.gif",
                   "https://cdn.discordapp.com/attachments/276667503034499072/309781525971337226/congaparrot.gif",
                   "https://cdn.discordapp.com/attachments/276667503034499072/309781549639794688/shuffleparrot.gif"]
        link = random.choice(parrots)
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
        print("Parrot sent!")
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
            if pos != -1 and received_string[pos + 1] != " ":
                print("Error:" + received_string[pos + 1])
                return
            pos = received_string.find("\"")
            if pos != -1:
                print("Error:" + received_string[pos + 1])
                return
            final_string = ""
            number_emoji = self.botVariables.numbersEmoji
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
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "http://quotesondesign.com/wp-json/posts?filter[orderby]=rand&filter[posts_per_page]=1") as resp:
                r = await resp.json()
        await self.bot.send_message(ctx.message.channel, "**" + BotMethods.cleanhtml("From " + r[0]['title'])
                                    + ":**" + html.unescape(BotMethods.cleanhtml(r[0]['content'])))

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
                await self.bot.send_message(ctx.message.channel,
                                            "**Translated text:**" + self.gs.translate(message_received, language))
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
    async def short(self, ctx, *args):
        """Generate a short url from the url given as parameter
        Usage: !short https://www.yoururl.blabla
        Example: !short https://www.google.it/imghp
        """
        if len(args) == 1:
            try:
                if ctx.message.server is not None:
                    print("Deleting the message...")
                    await self.bot.delete_message(ctx.message)
            except discord.errors.Forbidden:
                print("Can't delete the message...")
            short_url = await self.get_short_url(args[0])
            if short_url.startswith("Error"):  # An error occurred
                await self.bot.send_message(ctx.message.channel, "**An error occurred** " + short_url)
            else:
                await self.bot.send_message(ctx.message.channel, "**Your Short Url:** " + short_url +
                                            "\n (Generated by: " + ctx.message.author.mention + ")")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "short <longurl>, for more see " + self.command_prefix + "help short")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True, hidden=True)
    async def showcolor(self, ctx, *args):
        """Show an image with the given color code
        Usage: !showcolor #COLORHEX/(R,G,B)
        Example: !showcolor #ff0000
        Example: !showcolor (255, 0, 0)
        """
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
                await self.bot.send_message(ctx.message.channel,
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
                await self.bot.send_message(ctx.message.channel,
                                            "*An error occurred requesting the color... is your color code valid?*")
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
                await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "showcolor #COLORHEX/\"(R,G,B)\", for more see " + self.command_prefix + "help showcolor")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def lmgtfy(self, ctx, *args):
        """Generate a "let me google it for you" url
        Usage: !lmgtfy "search box"
        Example: !lmgtfy "hello world"
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
            url = "http://lmgtfy.com/?q=" + urllib.parse.quote(args[0])
            # prepare the request
            short_url = await self.get_short_url(url)
            await self.bot.send_message(ctx.message.channel, "**Your Url:** " + short_url +
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
                    for current_index in range(len(json_received[index]['DataClasses'])):
                        value_to_print += str(json_received[index]['DataClasses'][current_index]) + ", "
                    embed.add_field(name=str(json_received[index]['Title']), value=value_to_print, inline=False)
                embed.set_footer(text="Using haveibeenpwned.com")
                await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel,
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

    @commands.command(pass_context=True)
    async def ur(self, ctx, *args):
        """Search a word in the urban dictionary
        Usage: !ur <WORD>
        Usage: !ur <WORD> <NumberOfResults(default = 1)>
        Example: !ur dunno
        Example: !ur dunno 5
        """
        print("-------------------------")
        if len(args) == 1 or len(args) == 2:
            request_link = "http://api.urbandictionary.com/v0/define?term=" + str(args[0])
            async with aiohttp.ClientSession() as session:
                async with session.get(request_link) as resp:  # the website use get
                    request_result = await resp.json()
            if len(request_result["list"]) == 0:  # no results found
                print("No results for that word in urban dictionary")
                await self.bot.send_message(ctx.message.channel,
                                            "*No results found for \"" + str(args[0]) + "\" in urban dictionary*")
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
                    await self.bot.send_message(ctx.message.channel, embed=embed)
                    print("Ur embed sent successfully")
                except discord.errors.HTTPException:
                    print("HTTPException during the sending of ur embed")
                    await self.bot.send_message(ctx.message.channel, "*An error occurred sending the result...*")
        else:
            await self.bot.send_message(ctx.message.channel,
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

    @commands.command(pass_context=True)
    async def movievotes(self, ctx, *args):
        """Search the movie votes in metacritic database
        Usage: !movievotes <film Title>
        Example: !movievotes "Avengers: Infinity War"
        """
        print("-------------------------")
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
                        await self.bot.send_message(ctx.message.channel, "*An error occurred downloading the data...*")
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
                    await self.bot.send_message(ctx.message.channel, embed=embed)
                else:
                    print("No films found")
                    await self.bot.send_message(ctx.message.channel, "*No films found, check the name...*")
            else:
                print("No films found")
                await self.bot.send_message(ctx.message.channel, "*No films found, check the name...*")
        else:
            await self.bot.send_message(ctx.message.channel,
                                        "**Usage:** " + self.command_prefix + "movievotes <film Title>, for more see " + self.command_prefix + "help movievotes")
        print("-------------------------")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot
        self.botVariables = self.bot.bot_variables_reference
        # assigning variables value now i can use botVariables
        self.command_prefix = self.botVariables.command_prefix

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotCommonCommands(bot))
