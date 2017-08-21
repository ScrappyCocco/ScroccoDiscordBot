# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import html
import random
import discord
import requests
import goslate
import time

from discord.errors import HTTPException
from urllib import error
from datetime import datetime
from random import randint
from botVariablesClass import BotVariables
from botMethodsClass import BotMethods
# ---------------------------------------------------------------------


class BotCommonCommands:
    """ Class with Bot 'Gaming' commands (statistics for gamers) """
    # ---------------------------------------------------------------------

    botVariables = BotVariables(False)  # used for username and for emoji array
    gs = goslate.Goslate()  # translator

    # ---------------------------------------------------------------------

    @commands.command()
    async def gif(self, *args):
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
            r = requests.get("http://api.giphy.com/v1/gifs/random?api_key="+currentgifkey)
            await self.bot.say(r.json()['data']['image_url'])
        else:
            for x in range(0, len(args)):
                tag = tag + args[x]
                if x != (len(args) - 1):
                    tag += "+"
            print("Gif Request with arguments:" + tag)
            r = requests.get("http://api.giphy.com/v1/gifs/random?api_key="+currentgifkey+"&tag=" + tag)
            print("GifRequest:Found Length:" + str(len(r.json()['data'])))
            if (len(r.json()['data'])) == 0:
                await self.bot.say("No GIF found with those tags :frowning: ")
            else:
                await self.bot.say(r.json()['data']['image_url'])
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def cat(self):
        """Print a random cat
        Usage: !cat
        """
        r = requests.get("http://random.cat/meow")
        await self.bot.say(r.json()['file'])

    # ---------------------------------------------------------------------

    @commands.command()
    async def meme(self, *args):
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
                await self.bot.say("The third param it's not a number!")
                error_count = 1
                print("GenID Not Correct")
        if 3 >= len(args) > 0 == error_count:
            if len(args) < 3 and generator_id == 0:
                r = requests.get(generator_link)
                generator = r.json()
                if generator['success']:
                    generator_id = generator['data']['memes'][random.randint(0, len(generator['data']['memes']) - 1)]['id']
                else:
                    print("Error getting meme generators")
            r = requests.post("https://api.imgflip.com/caption_image",
                              data={'template_id': int(generator_id),
                                    'username': self.botVariables.get_meme_generator_username(),
                                    'password': self.botVariables.get_meme_generator_password(),
                                    'text0': phrase1,
                                    'text1': phrase2})
            result = r.json()
            if result['success']:
                await self.bot.say(str(result['data']['url']) + " ID Meme:" + str(generator_id))
            else:
                print("Error:" + str(result['error_message']))
        else:
            await self.bot.say("**Usage:** !meme \"text1\" \"text2 or memeId\"[Optional] \"memeId\"[Optional]")
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
        await self.bot.say(embed=embed)
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command()
    async def printtext(self, *args):
        """Print a phrase with emotes
        Usage: !printtext "Hello there"
        """
        if len(args) == 1:
            received_string = args[0]
            if received_string.startswith('"') and received_string.endswith('"'):
                received_string = received_string[1:-1]
            pos = received_string.find("\\")
            if not pos == -1:
                if not received_string[pos + 1] == " ":
                    print("Error:" + received_string[pos + 1])
                    return
            pos = received_string.find("\"")
            if not pos == -1:
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
            await self.bot.say(final_string)
        else:
            await self.bot.say("**Usage:** !printtext \"phrase\"")

    # ---------------------------------------------------------------------

    @commands.command()
    async def quote(self):
        """Print a random quote
        Usage: !quote
        """
        r = requests.get("http://quotesondesign.com/wp-json/posts?filter[orderby]=rand&filter[posts_per_page]=1")
        await self.bot.say(
            "**" + BotMethods.cleanhtml("From " + r.json()[0]['title']) + ":**" + html.unescape(
                BotMethods.cleanhtml(r.json()[0]['content'])))

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
            await self.bot.send_message(ctx.message.channel, "**Usage:** !translate \"message\" language(it/en/de...)")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def weather(self, ctx, *args):
        """Print the current weather in a given city
        (0 is now, 1 is 12h later, 2 tomorrow, ...., 19 is the max[12h for 10 days])
        (the country code is in ISO-3166 = 2 letters)
        Usage: !weather Venice
        Usage: !weather IT Rome
        Usage: !weather Rome 1
        Usage: !weather DE Berlin 1
        """
        if len(args) < 1 or len(args) > 3:
            await self.bot.say("**Please read:** !help weather")
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
                            await self.bot.say("**Check the day code, please read:** !help weather")
                            return
                    else:
                        city_name = str(args[1])
                if len(args) == 3:
                    if not country_code:
                        await self.bot.say("**Check the country code, please read:** !help weather")
                        return
                    else:
                        city_name = str(args[1])
                        try:
                            day = int(args[2])
                        except ValueError:
                            await self.bot.say("**Check the day code, please read:** !help weather")
                            return
            if day > 19:
                await self.bot.say("**Check the day code, please read:** !help weather")
                return
            # I've everything now, starting getting the weather
            print("-------------------------")
            print("Making weather request")
            half_day = BotMethods.convert_hours_to_day(day)  # this because the weather is divided in 10 days and 20 times 12h
            url = "http://api.wunderground.com/api/"+self.botVariables.get_weather_key()+"/"
            # url += "forecast/q/"+country_code_str+"/"+city_name+".json" old weather, before the 10 days
            url += "forecast10day/q/" + country_code_str + "/" + city_name + ".json"
            r = requests.get(url)
            request_result = r.json()  # convert the response to a json file
            try:
                await self.bot.say("**Error:** "+str(request_result["response"]["error"]["description"]) + "(check usage with !help weather)")
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
                    await self.bot.say(final_message)
                    return
                print("No errors found in request, creating embed")
                day_name = str(request_result["forecast"]["txt_forecast"]["forecastday"][day]["title"])
                day_number = str(request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["date"]["day"])
                month_number = str(request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["date"]["month"])
                year_number = str(request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["date"]["year"])
                embed = discord.Embed(title="Weather",
                                      colour=discord.Colour(0x088DA5),
                                      url="https://www.wunderground.com/",
                                      description="Weather in \"" + city_name + "\" during \"" + day_name + "\" " + day_number+"/"+month_number+"/"+year_number,
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
                    temp_min = request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["low"]["celsius"]
                except KeyError:
                    temp_min = "Not found..."
                embed.add_field(name="Min Temperature:", value=temp_min, inline=True)

                try:
                    # max temperature of the day
                    temp_max = request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["high"]["celsius"]
                except KeyError:
                    temp_max = "Not found..."
                embed.add_field(name="Max Temperature:", value=temp_max, inline=True)

                try:
                    # Average Humidity temperature of the day
                    avg_humid = str(request_result["forecast"]["simpleforecast"]["forecastday"][half_day]["avehumidity"]) + "%"
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
                    await self.bot.say(embed=embed)
                except HTTPException:
                    await self.bot.say("*A strange error occurred, cannot retrieve that city, sorry...*")
            print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def hacked(self, ctx, *args):
        """Check if the email or the username have been hacked
        Usage: !hacked test@test.it
        """
        print("-------------------------")
        if len(args) == 1:
            try:
                if ("!hacked" in ctx.message.content) and (ctx.message.server is not None):
                    print("Deleting the message...")
                    await self.bot.delete_message(ctx.message)
            except discord.errors.Forbidden:
                print("Can't delete the message...")
            url = "https://haveibeenpwned.com/api/v2/breachedaccount/"
            print("Request:" + url + "Email")
            r = requests.get(url + str(args[0]))  # the website use get
            if str(r) == "<Response [404]>":
                print("Not found")
                embed = discord.Embed(title="Hacked?", url='https://haveibeenpwned.com/', color=0x2fea00)
                embed.set_author(name="Analysis required by " + ctx.message.author.name,
                                 icon_url=ctx.message.author.avatar_url)
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/276674976210485248/304961315326394369/1492796826_Tick_Mark_Dark.png')
                embed.add_field(name="Result:", value="Everything is k! No problems found", inline=False)
                embed.set_footer(text="Using haveibeenpwned.com")
                await self.bot.say(embed=embed)
            else:
                json_received = r.json()
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
                await self.bot.say(embed=embed)
        else:
            await self.bot.say("**Usage:** !hacked \"email or username\"")
        print("-------------------------")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotCommonCommands(bot))
