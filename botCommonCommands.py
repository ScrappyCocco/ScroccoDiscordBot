# ---------------------------------------------------------------------
# IMPORTS

from discord.ext import commands

import html
import random
import discord
import requests
import goslate

from urllib import error
from random import randint
from botVariablesClass import BotVariables
from botMethodsClass import BotMethods
# ---------------------------------------------------------------------


class BotCommonCommands:
    """ Class with Bot 'Gaming' commands (statistics for gamers) """
    # ---------------------------------------------------------------------

    botVariables = BotVariables()  # used for username and for emoji array
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
        example 1:'!meme "Hello there Discord" 47235368'
        example 2:'!meme "Hello there Discord" "How are you?" 47235368'
        """
        print("-------------------------")
        error = 0
        genID = 0
        Phrase1 = ""
        Phrase2 = ""
        genLink = "https://api.imgflip.com/get_memes"
        if len(args) == 1:
            Phrase1 = args[0]
            print("Param1:" + Phrase1)
        if len(args) > 1:
            Phrase1 = args[0]
            print("Param2:" + Phrase1)
            try:
                genID = int(args[1])
                print("GenID:" + str(genID))
            except ValueError:
                Phrase2 = args[1]
                print("Param2 - not a number")
        if len(args) == 3:
            try:
                genID = int(args[2])
                print("GenID:" + str(genID))
            except ValueError:
                await self.bot.say("The third param it's not a number!")
                error = 1
                print("GenID Not Correct")
        if 3 >= len(args) > 0 == error:
            if len(args) < 3 and genID == 0:
                r = requests.get(genLink)
                generator = r.json()
                if generator['success']:
                    genID = generator['data']['memes'][random.randint(0, len(generator['data']['memes']) - 1)]['id']
                else:
                    print("Error getting meme generators")
            r = requests.post("https://api.imgflip.com/caption_image",
                              data={'template_id': int(genID),
                                    'username': self.botVariables.memeGeneratorUsername,
                                    'password': self.botVariables.memeGeneratorPassword,
                                    'text0': Phrase1,
                                    'text1': Phrase2})
            result = r.json()
            if result['success']:
                await self.bot.say(str(result['data']['url']) + " ID Meme:" + str(genID))
            else:
                print("Error:" + str(result['error_message']))
        else:
            await self.bot.say("**Usage:** !meme <text1> <text2 or memeId>[Optional] <memeId>[Optional]")
        print("-------------------------")

    # ---------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def party(self, ctx):
        """Party Hard Command
        Usage: !party
        """
        print("-------------------------")
        normalParrot = "https://cdn.discordapp.com/attachments/276674976210485248/304557572416077824/parrot.gif"
        congaParrot = "https://cdn.discordapp.com/attachments/276667503034499072/309781525971337226/congaparrot.gif"
        shuffleParrot = "https://cdn.discordapp.com/attachments/276667503034499072/309781549639794688/shuffleparrot.gif"
        link = ""
        number = randint(0, 2)
        print("Number:" + str(number))
        if number == 0:
            link = normalParrot
        if number == 1:
            link = congaParrot
        if number == 2:
            link = shuffleParrot
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
            receivedString = args[0]
            if receivedString.startswith('"') and receivedString.endswith('"'):
                receivedString = receivedString[1:-1]
            pos = receivedString.find("\\")
            if not pos == -1:
                if not receivedString[pos + 1] == " ":
                    print("Error:" + receivedString[pos + 1])
                    return
            pos = receivedString.find("\"")
            if not pos == -1:
                print("Error:" + receivedString[pos + 1])
                return
            # print(str(stringa))
            finalString = ""
            numbersEmoji = self.botVariables.numbersEmoji
            for c in receivedString:
                # print(c)
                if c.isalnum():
                    try:
                        val = int(c)
                        if val < 10:
                            finalString += numbersEmoji[val] + " "
                        else:
                            print("fatal Error!!!-" + str(val))

                    except ValueError:
                        c = c.lower()
                        if c == "è" or c == "é" or c == "à" or c == "ù" or c == "ì":
                            finalString += c + " "
                        else:
                            finalString += ":regional_indicator_" + c + ":" + " "
                else:
                    if c == "!" or c == "?" or c == "#":
                        if c == "!":
                            finalString += ":exclamation:" + " "
                        else:
                            if c == "#":
                                finalString += ":hash:" + " "
                            else:
                                finalString += ":question:" + " "
                    else:
                        finalString += c + " "
            await self.bot.say(finalString)
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
            messageReceived = str(args[0])
            language = str(args[1])
            try:
                await self.bot.send_message(ctx.message.channel, self.gs.translate(messageReceived, language))
            except error.HTTPError:
                await self.bot.send_message(ctx.message.channel, "HTTP Error 503: Service Unavailable")
        else:
            await self.bot.send_message(ctx.message.channel, "**Usage:** !translate <\"message\"> <language(it/en/de...)>")

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
                print("Can't delete the message(I need 2FA?)...")

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
                jsonCodeReceived = r.json()
                print(len(jsonCodeReceived))
                embed = discord.Embed(title="Hacked?", url='https://haveibeenpwned.com/',
                                      description="Websites where you are registered that have been hacked:",
                                      color=0xff0000)
                embed.set_author(name="Analysis required by " + ctx.message.author.name,
                                 icon_url=ctx.message.author.avatar_url)
                embed.set_thumbnail(
                    url='https://cdn.discordapp.com/attachments/276674976210485248/304963039545786368/1492797249_shield-error.png')
                for index in range(len(jsonCodeReceived)):
                    valueToPrint = "**Website:** " + str(jsonCodeReceived[index]['Domain']) + "\n**Date:** " + str(
                        jsonCodeReceived[index]['BreachDate'])
                    valueToPrint += "\n**Stolen:** "
                    for currentIndex in range(len(jsonCodeReceived[index]['DataClasses'])):
                        valueToPrint += str(jsonCodeReceived[index]['DataClasses'][currentIndex]) + ", "
                    embed.add_field(name=str(jsonCodeReceived[index]['Title']), value=valueToPrint, inline=False)
                embed.set_footer(text="Using haveibeenpwned.com")
                await self.bot.say(embed=embed)
        else:
            await self.bot.say("**Usage:** !hacked <email or username>")
        print("-------------------------")

    # ---------------------------------------------------------------------

    def __init__(self, bot):
        print("CALLING CLASS-->" + self.__class__.__name__ + " class called")
        self.bot = bot

    def __del__(self):
        print("DESTROYING CLASS-->" + self.__class__.__name__ + " class called")


def setup(bot):
    bot.add_cog(BotCommonCommands(bot))
