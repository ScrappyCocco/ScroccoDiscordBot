# ---------------------------------------------------------------------
# IMPORTS

from botVariablesClass import BotVariables
from botMethodsClass import BotMethods

import discord  # pip install discord.py
import requests
import websockets
import aiohttp
import urllib.parse

from discord.ext import commands

# ---------------------------------------------------------------------
# INITIALIZATION

botVariables = BotVariables(True)  # create class checking the JSON file

cleverbot_api_key = botVariables.get_clever_key()

bot_command_prefix_string = botVariables.get_command_prefix()  # get the command prefix

# creation of bot prefix and description
bot = commands.Bot(command_prefix=bot_command_prefix_string, description=botVariables.get_description())
bot.get_command("help").hidden = True  # hiding the !help command

# getting base informations
privateMessagesOwner = botVariables.get_owner_private_messages()
startUpExtensions = botVariables.get_startup_extensions()


# ---------------------------------------------------------------------
# NECESSARY FUNCTIONS


# function that create bot attributes
def attributes_initialization(default_status: str):
    print("---Creating bot attributes---")
    setattr(bot, 'maintenanceMode', False)
    setattr(bot, 'lastInGameStatus', str(default_status))
    setattr(bot, 'cleverbot_cs_parameter', "")
    setattr(bot, 'cleverbot_reply_number', 0)
    print("---Finished creating attributes---")
    print("------------------------")


# function that send a message when users use private chat with bot the first time
async def first_chat_alert(channel, user):
    if (channel.type != discord.ChannelType.private) or (privateMessagesOwner == "") or (
            str(user.id) == privateMessagesOwner):  # if the function is not active
        return False
    else:
        user_id = user.id
        if user_id not in botVariables.privateChatUsers:  # if is the first time
            botVariables.privateChatUsers.append(user_id)  # add the user ID to the array
            message_sent = await bot.send_message(channel,
                                                  " :exclamation:  :exclamation:  :exclamation: :exclamation: :exclamation: \n" +
                                                  "**" + botVariables.get_private_chat_alert() + "**\n" +
                                                  " **(As your first message here, it's not processed)**\n " +
                                                  " :exclamation:  :exclamation:  :exclamation: :exclamation: :exclamation:  \n ")
            try:
                if len(await bot.pins_from(channel)) == 0:  # only if we begin the chat
                    await bot.pin_message(message_sent)  # pins the message because is important
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                print("ERROR pinning the message")
            return True  # i send the warning
        else:  # message already sent
            return False


# function that forward the non-command message to bot owner (if the function is active)
async def forwards_message(message):
    if message.channel.name is None:
        # send private message to bot owner if possible
        if (str(message.author.id) != privateMessagesOwner) and (
                privateMessagesOwner != ""):  # not sending messages to myself or not if the function is not active
            if len(message.attachments) > 0:  # not sending attachments
                await bot.send_message(message.channel,
                                       "***Remember that attachments ARE NOT sent to bot owner... Message has not been sent!***")
            else:
                await bot.send_message(discord.User(id=privateMessagesOwner),
                                       "Message from " + str(message.author.name) + "(ID=" + str(
                                           message.author.id) + "):" + message.content)


# cleverbot async request - more faster than using the wrapper
async def cleverbot_request(channel, cleverbot_question):
    formatted_question = urllib.parse.quote(cleverbot_question)  # convert question into url-string
    if bot.cleverbot_cs_parameter == "":
        request_url = "http://www.cleverbot.com/getreply?key=" + cleverbot_api_key + "&input=" + formatted_question
    else:
        request_url = "http://www.cleverbot.com/getreply?key=" + cleverbot_api_key + "&input=" + formatted_question + "&cs=" + bot.cleverbot_cs_parameter
    response_error = False
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(request_url) as response:
            try:
                content = await response.json()
            except UnicodeDecodeError:  # JSON ERROR
                print("CLEVERBOT ERROR")
                response_error = True
                try:
                    print("Cleverbot Attempt 1 - using read()...\n\n")
                    content = str(await response.read())
                except UnicodeDecodeError:
                    try:
                        print("Cleverbot Attempt 2 - using content()...\n\n")
                        content = str(await response.content())
                    except UnicodeDecodeError:
                        await bot.send_message(channel,
                                               "*Cleverbot fatal error, please use " + bot_command_prefix_string + "clearclever")
                        return
    if response_error:  # an error occurred (JSON NOT CORRECT - USE THE CONTENT AS A STRING)
        start_pos = content.find("\"output\":\"") + 10
        end_pos = content.find("\"conversation_id\":") - 2
        if start_pos == -1 or end_pos == -1:
            print("Error calculating sub-string positions")
        else:
            reply = content[start_pos:start_pos + (end_pos - start_pos)]  # calculate cleverbot reply substring
            await bot.send_message(channel, reply)
        clear_cleverbot_parameters()  # clear cleverbot to begin a new conversation
    else:  # normal cleverbot reply (json file)
        request_result_cs = content["cs"]
        print("Cleverbot interaction number:" + content["interaction_count"])
        if bot.cleverbot_cs_parameter != request_result_cs and int(
                content["interaction_count"]) > bot.cleverbot_reply_number:
            bot.cleverbot_reply_number = int(content["interaction_count"])
            bot.cleverbot_cs_parameter = request_result_cs
        await bot.send_message(channel, content["output"])


# ---------------------------------------------------------------------
# bot "on_message" event, called when a message is created and sent to a server.


@bot.event
async def on_message(message):
    try:
        if message.author.bot:  # nothing to do, the message is from me
            return
        # ---------------------------------------------------------------------
        if await first_chat_alert(message.channel, message.author):
            return
        # ---------------------------------------------------------------------
        # get bot mention
        if message.server is None:
            mention = bot.user.mention
        else:
            mention = message.server.me.mention
        if len(message.mentions) >= 1:  # message starts with a mention, check if it's mine
            if message.content.startswith(mention):  # yes the message starts with a mention, it's me?
                new_message = message.content.replace(str(mention), "",
                                                      1)  # remove the mention from the message (only 1)
                # new_message = new_message[1:]  # remove the additional space (not necessary)
                for found_mention in message.mentions:  # convert all mentions to names to make the message clear
                    new_message = new_message.replace(str(found_mention.mention), str(found_mention.name))
                # ---------------------------------------------------------------------
                if bot.maintenanceMode and not BotMethods.is_owner(message.author):  # if it's in maintenance Mode
                    return
                new_message = new_message.lstrip()  # remove additional spaces from cleverbot question (before and after)
                print("Cleverbot Question received, asking cleverbot...")
                await cleverbot_request(message.channel, new_message)
                print("-------------------------")
            else:  # the message don't start with a mention, maybe it's a command?
                try:
                    if bot.maintenanceMode and not BotMethods.is_owner(
                            message.author):  # if it's in maintenance Mode then quit
                        return
                    if message.content.startswith(
                            bot_command_prefix_string):  # if starts with command-prefix then process as command
                        await bot.process_commands(message)  # tell the bot to try to execute the command
                    else:  # forward the message (if active)
                        await forwards_message(message)
                except discord.ext.commands.errors.CommandNotFound:  # command doesn't exist
                    print("Command not found...")
        else:
            if message.content.find("\\") == -1:  # error check for special chars
                try:
                    if bot.maintenanceMode and not BotMethods.is_owner(
                            message.author):  # if it's in maintenance Mode then quit
                        return
                    if message.content.startswith(
                            bot_command_prefix_string):  # if starts with command-prefix then process as command
                        await bot.process_commands(message)  # tell the bot to try to execute the command
                    else:  # forward the message (if active)
                        await forwards_message(message)
                except discord.ext.commands.errors.CommandNotFound:  # command doesn't exist
                    print("Command not found...")

    except discord.ext.commands.errors.BadArgument:
        print("Error 2 executing the command...")
        return


# ---------------------------------------------------------------------


@bot.command(pass_context=True)
async def hello(ctx):
    """Hello command - simple command for testing"""
    await bot.send_message(ctx.message.channel, "Hello " + ctx.message.author.name + "!")


# ---------------------------------------------------------------------
# function that clear cleverbot parameters to create a new conversation to avoid errors
# this function is separated from the command (clearclever) because then i can call it on cleverbot errors in on_message()
def clear_cleverbot_parameters():
    print("Cleaning...")
    if bot.cleverbot_cs_parameter != "":
        bot.cleverbot_cs_parameter = ""
        bot.cleverbot_reply_number = 0
        return True
    else:
        print("Can't clean cleverbot chat")
        return False


@bot.command(pass_context=True, hidden=True)
async def clearclever(ctx):
    """Clean Cleverbot Conversation"""
    print("-------------------------")
    print("Cleaning...")
    if clear_cleverbot_parameters():
        await bot.send_message(ctx.message.channel, "*Cleaning Complete*")
    else:
        print("Can't clean cleverbot chat")
    print("End of cleaning")
    print("-------------------------")


# ---------------------------------------------------------------------
# bot "on_ready" event, called when the client is done preparing the data received from Discord


@bot.event
async def on_ready():
    print("------------------------")
    print('Logged as:' + bot.user.name + " ID:" + bot.user.id)
    url = botVariables.get_server_read_status_url()
    try:
        if botVariables.emptyUrl not in url:
            r = requests.get(url)  # get the last in-game status from server
            if r.text != "Error" and r.status_code == 200:
                print("No Error - changing state to:" + r.text)
                await bot.change_presence(game=discord.Game(name=r.text))
                bot.lastInGameStatus = r.text
            else:
                print("Request error - changing status to default")
                await bot.change_presence(game=discord.Game(name=botVariables.get_default_status()))
        else:
            print("URL request error - changing status to default - check bot data json file")
            await bot.change_presence(game=discord.Game(name=botVariables.get_default_status()))
    except websockets.exceptions.ConnectionClosed:
        print("ERROR trying to change bot status")
    print("------------------------")


# ---------------------------------------------------------------------
# bot "on_reaction_add" event, called when a message has a reaction added to it


@bot.event
async def on_reaction_add(reaction, user):
    if user != bot.user:  # if is not me
        print("------------------------")
        if isinstance(reaction.emoji, str):
            print("Adding my reaction to the message... (Emoji: " + reaction.emoji + ")")
        else:
            if isinstance(reaction.emoji, discord.Emoji):
                print("Adding my reaction to the message... (Emoji Object: " + reaction.emoji.name + ")")
            else:
                print("UNKNOWN EMOJI OBJECT, ABORTING ADDING REACTION")
                return
        try:  # try adding my reaction
            await bot.add_reaction(reaction.message, reaction.emoji)
        except discord.errors.Forbidden:
            print("Can't add my reaction")
        print("------------------------")


# ---------------------------------------------------------------------
# bot "on_typing" event, Called when someone begins typing a message.
# doesn't works good in private chat


@bot.event
async def on_typing(channel, user, when):
    await first_chat_alert(channel, user)


# ---------------------------------------------------------------------
# MAIN EXECUTION (STARTUP AND SHUTDOWN)
if str(__name__) == "__main__":
    print("ACTION-->Loading bot, importing extensions...")
    print(startUpExtensions)
    print("------------------------")
    for extension in startUpExtensions:
        print("LOADING-->" + extension)
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('LOADING FAIL-->Failed to load extension {}\n{}'.format(extension, exc))
        print("------------------------")
    attributes_initialization(botVariables.get_default_status())
    print("ACTION-->Bot Login... Please Wait...")
    if botVariables.get_bot_distribution():  # is the bot in beta?
        bot.run(botVariables.get_discord_bot_token(True))  # token beta Bot
    else:
        bot.run(botVariables.get_discord_bot_token(False))  # token Final Bot

    # END OF PROGRAM

    for extension in startUpExtensions:
        print("UNLOADING-->" + extension)
        try:
            bot.unload_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('UNLOADING FAIL-->Failed to unload extension {}\n{}'.format(extension, exc))

    print("ACTION-->End of program")
