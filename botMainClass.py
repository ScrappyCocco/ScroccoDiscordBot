# ---------------------------------------------------------------------
# IMPORTS

from botVariablesClass import BotVariables
from botMethodsClass import BotMethods

import discord  # pip install discord.py
import requests
import json
import websockets

from cleverwrap import CleverWrap
from discord.ext import commands

# ---------------------------------------------------------------------
# INITIALIZATION

botVariables = BotVariables(True)

cw = CleverWrap(botVariables.get_clever_key())  # clever api object

# creation of bot prefix and description
bot = commands.Bot(command_prefix=botVariables.get_command_prefix(), description=botVariables.get_description())
bot.get_command("help").hidden = True  # hiding the !help command

privateMessagesOwner = botVariables.get_owner_private_messages()
maxCleverbotRequests = botVariables.get_max_cleverbot_requests()
startUpExtensions = botVariables.get_startup_extensions()

# ---------------------------------------------------------------------


@bot.event
async def on_message(message):
    try:
        if message.author.bot:  # nothing to do
            return
        else:
            if message.channel.name is None:
                # send private message to bot owner
                if not str(message.author.id) == privateMessagesOwner:
                    await bot.send_message(discord.User(id=privateMessagesOwner), "Message from " + str(message.author.name) + "(ID=" + str(message.author.id) + "):" + message.content)
            # ---------------------------------------------------------------------
        if message.server is None:
            mention = bot.user.mention
        else:
            mention = message.server.me.mention
        if message.content.startswith("<"):  # message starts with a mention, check if it's mine
            if mention[2] == '!' and message.content[2] != '!':  # from mobile the mention has a !
                new_string = "<@!" + message.content[2:]
                string_to_compare = new_string
            else:
                string_to_compare = message.content
            if string_to_compare.startswith(mention):  # yes the message starts with a mention
                new_message = message.content[22:]  # get the cleverbot question
                # ---------------------------------------------------------------------
                if bot.maintenanceMode and not BotMethods.is_owner(message.author):  # if it's in maintenance Mode
                    return
                print("-------------------------")
                new_message = new_message.lstrip()  # remove additional spaces from cleverbot question
                print("Cleverbot Question:" + new_message)
                reply = ""
                try:
                    request_index = 0
                    # i have to wait for a complete reply(errors could happen with that api)
                    while reply == "" and request_index < maxCleverbotRequests:
                        reply = cw.say(new_message)
                        print("Cleverbot Reply:" + reply)
                        request_index += 1
                    if reply == "":
                        await bot.send_message(message.channel, "Cleverbot error")  # send the cleverbot response
                    else:
                        print("-------------------------")
                        await bot.send_message(message.channel, reply)  # send the cleverbot response
                except json.decoder.JSONDecodeError:  # an error occurred
                    if botVariables.indexError == 0:  # first error
                        print("Cleaning Cleverbot...")
                        botVariables.indexError += 1
                        if cw:  # try cleaning cleverbot history
                            cw.reset()
                        else:
                            print("Cleaning Cleverbot...")
                        print("Cleaning Done")
                    else:  # error it's > 0
                        await bot.send_message(message.channel, "*Cleverbot fatal error...*")
                    print("-------------------------")
            else:  # the message don't start with a mention, maybe it's a command?
                try:
                    if bot.maintenanceMode and not BotMethods.is_owner(message.author):  # if it's in maintenance Mode
                        return
                    await bot.process_commands(message)  # tell the bot to try to execute the command
                except discord.ext.commands.errors.CommandNotFound:  # command doesn't exist
                    print("Command not found...")
        else:
            if message.content.find("\\") == -1:
                try:
                    if bot.maintenanceMode and not BotMethods.is_owner(message.author):  # if it's in maintenance Mode
                        return
                    await bot.process_commands(message)  # tell the bot to try to execute the command
                except discord.ext.commands.errors.CommandNotFound:  # command doesn't exist
                    print("Command not found...")
            else:
                if message.content.startswith("!"):
                    if message.channel.name is not None:
                        print("Error 1 executing the command...")

    except discord.ext.commands.errors.BadArgument:
        print("Error 2 executing the command...")
        return

# ---------------------------------------------------------------------


@bot.command(pass_context=True)
async def hello(ctx):
    """Hello command - simple command for testing"""
    await bot.say("Hello " + ctx.message.author.name + "!")


# ---------------------------------------------------------------------

@commands.command(hidden=True)
async def clearclever():
    """Clean Cleverbot Conversation"""
    print("-------------------------")
    print("Cleaning...")
    if cw:
        cw.reset()
        botVariables.indexError = 0
    else:
        print("Can't clean cleverbot chat")
    print("End of cleaning")
    print("-------------------------")

# ---------------------------------------------------------------------


@bot.event
async def on_ready():
    print("------------------------")
    print('Logged as:' + bot.user.name + " ID:" + bot.user.id)
    url = botVariables.get_server_read_status_url()
    try:
        r = requests.get(url)  # get the last in-game status from server
        if r.text != "Error":
            setattr(bot, 'lastInGameStatus', str(r.text))
            print("No Error - changing state to:" + r.text)
            await bot.change_presence(game=discord.Game(name=r.text))
        else:
            print("Request error - changing status to default")
            await bot.change_presence(game=discord.Game(name=botVariables.get_default_status()))
    except websockets.exceptions.ConnectionClosed:
        print("ERROR trying to change bot status")
    print("------------------------")

# ---------------------------------------------------------------------
# MAIN EXECUTION (STARTUP AND SHUTDOWN)
if str(__name__) == "__main__":
    print("ACTION-->Loading bot, importing extensions...")
    print(startUpExtensions)
    setattr(bot, 'maintenanceMode', False)
    print("------------------------")
    for extension in startUpExtensions:
        print("LOADING-->"+extension)
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('LOADING FAIL-->Failed to load extension {}\n{}'.format(extension, exc))
        print("------------------------")

    print("ACTION-->Bot Login...")
    # bot.run(botVariables.get_discord_bot_token(False))  # token Final Bot
    bot.run(botVariables.get_discord_bot_token(True))  # token beta Bot

    # END OF PROGRAM

    for extension in startUpExtensions:
        print("UNLOADING-->"+extension)
        try:
            bot.unload_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('UNLOADING FAIL-->Failed to unload extension {}\n{}'.format(extension, exc))
    # cleaning some var(s)
    del botVariables
    del cw

    print("ACTION-->End of program")
