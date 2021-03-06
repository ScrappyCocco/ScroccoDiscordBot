#!/usr/bin/env python3
# ---------------------------------------------------------------------
# CHANGING DIR
import os

if not os.getcwd().endswith("src"):
    os.chdir("src")
# ---------------------------------------------------------------------
# IMPORTS

import hypixel  # must be here to be loaded first
from discord.ext import commands

import discord  # pip install discord.py
import requests
import websockets
import aiohttp
import urllib.parse

from botVariablesClass import BotVariables
from botMethodsClass import BotMethods

# ---------------------------------------------------------------------
# INITIALIZATION

botVariables = BotVariables(True)  # create class checking the JSON file

cleverbot_api_key = botVariables.get_clever_key()

bot_command_prefix_string = botVariables.get_command_prefix()  # get the command prefix

# Set intents permissions
intents = discord.Intents.all()

# creation of bot prefix and description
bot = commands.Bot(command_prefix=bot_command_prefix_string,
                   description=botVariables.get_description(),
                   intents=intents)
bot.get_command("help").hidden = True  # hiding the !help command

# getting base informations
privateMessagesOwner = botVariables.get_owner_private_messages()
startUpExtensions = botVariables.get_startup_extensions()


# ---------------------------------------------------------------------
# NECESSARY FUNCTIONS

# function that create bot attributes i need before loading the bot extensions
def pre_extension_attributes_initialization():
    print("---Creating pre_extension bot attributes---")
    bot.bot_variables_reference = botVariables
    print("---Finished creating pre_extension attributes---")
    print("------------------------")


# function that create the others bot attributes
def after_extension_attributes_initialization(default_status: str):
    print("---Creating after_extension bot attributes---")
    setattr(bot, 'maintenanceMode', False)  # used to determine if the bot is in maintenance status
    # Informations about the in-game status
    setattr(bot, 'hasAListOfStates', False)  # used to determine if the bot has more than a status
    setattr(bot, 'listOfStates', [])  # used to store the list of the possible statuses
    setattr(bot, 'lastInGameStatus', str(default_status))  # used to save the in-game status
    setattr(bot, 'isInStreamingStatus', False)  # used to check if the bot is in streaming status
    # cleverbot parameters, used for cleverbot discussion
    setattr(bot, 'cleverbot_cs_parameter', "")
    setattr(bot, 'cleverbot_reply_number', 0)
    print("---Finished creating after_extension attributes---")
    print("------------------------")


# Function that download the status of the bot (or use the default bot status if not possible)
async def download_and_set_first_status():
    url = botVariables.get_server_read_status_url()
    try:
        if botVariables.get_bot_save_state_to_server():
            r = requests.get(url)  # get the last in-game status from server
            print("Change State - HTTP Request Status Code:" + str(r.status_code))
            if r.text != "Error" and r.status_code == 200:
                print("No Error in the download - changing state...")
                state_string = r.text
            else:
                print("Request error - changing status to default")
                state_string = botVariables.get_default_status()
        else:
            if botVariables.get_bot_save_state_to_file():
                try:
                    file = open(botVariables.get_bot_save_state_file_name(), "r")
                    state_string = file.readline()
                    print("Status file successfully opened and read")
                except FileNotFoundError:
                    print("Cannot read file " + botVariables.get_bot_save_state_file_name() + " - FileNotFoundError")
                    state_string = botVariables.get_default_status()
            else:
                print("No save state on file or server found - changing status to default - check bot data json file")
                state_string = botVariables.get_default_status()
        if state_string.startswith("{") and state_string.endswith("}"):
            print("List of states found, saving and randomizing status...")
            # Save that is a list
            bot.hasAListOfStates = True
            # Save the list removing the {} and splitting the text
            bot.listOfStates = BotMethods.create_list_from_states_string(state_string)
            # Randomize and use the state
            state_to_use = BotMethods.get_random_bot_state(bot.listOfStates)
            await bot.change_presence(activity=discord.Game(name=state_to_use))
            bot.lastInGameStatus = state_to_use
        else:
            bot.hasAListOfStates = False
            bot.lastInGameStatus = state_string
            await bot.change_presence(activity=discord.Game(name=state_string))
        print("Status changed to " + str(bot.lastInGameStatus))
    except websockets.exceptions.ConnectionClosed:
        print("ERROR trying to change bot status")


# function that send a message when users use private chat with bot the first time
async def first_chat_alert(channel: discord.abc.Messageable, user: discord.User):
    if not isinstance(channel, discord.DMChannel) or (privateMessagesOwner == "") or (
            str(user.id) == privateMessagesOwner):  # if the function is not active
        return False
    else:
        user_id = user.id
        if user_id not in botVariables.private_chat_users:  # if is the first time
            botVariables.private_chat_users.append(user_id)  # add the user ID to the array
            message_sent = await channel.send(
                " :exclamation:  :exclamation:  :exclamation: :exclamation: :exclamation: \n" +
                "**" + botVariables.get_private_chat_alert() + "**\n" +
                " **(As your first message here, it's not processed)**\n " +
                " :exclamation:  :exclamation:  :exclamation: :exclamation: :exclamation:  \n ")
            try:
                if len(await channel.pins()) == 0:  # only if we begin the chat
                    await message_sent.pin()  # pins the message because is important
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                print("ERROR pinning the message")
            return True  # i send the warning
        else:  # message already sent
            return False


# function that forward the non-command message to bot owner (if the function is active)
async def forwards_message(message: discord.message):
    # send private message to bot owner if possible
    if (str(message.author.id) != privateMessagesOwner) and (
            privateMessagesOwner != ""):  # not sending messages to myself or not if the function is not active
        print("forwards_message() passed first if")
        if len(message.attachments) > 0:  # there are attachments in the message
            url_list = ""
            for attach in message.attachments:
                url_list += str(attach.url) + " - "  # create a sting with attachments urls
            user = bot.get_user(int(privateMessagesOwner))
            channel = user.dm_channel
            if channel is None:
                await user.create_dm()
                channel = user.dm_channel
            print("Forwarding message.attachments")
            await channel.send("Message from " + str(message.author.name) + "(ID=" + str(
                message.author.id) + "):" + message.content + "\nAttachments: " + url_list)
            await message.channel.send("***Message with attachments has been forwarded!***")
        else:  # not sending attachments
            user = bot.get_user(int(privateMessagesOwner))
            channel = user.dm_channel
            if channel is None:
                await user.create_dm()
                channel = user.dm_channel
            print("Forwarding standard message")
            await channel.send(
                "Message from " + str(message.author.name) + "(ID=" + str(message.author.id) + "):" + message.content)


# cleverbot async request - more faster than using the wrapper
async def cleverbot_request(channel: discord.abc.Messageable, cleverbot_question: str):
    formatted_question = urllib.parse.quote(cleverbot_question)  # convert question into url-string
    if bot.cleverbot_cs_parameter == "":
        request_url = "http://www.cleverbot.com/getreply?key=" + cleverbot_api_key + "&input=" + formatted_question
    else:
        request_url = "http://www.cleverbot.com/getreply?key=" + cleverbot_api_key + "&input=" + formatted_question + "&cs=" + bot.cleverbot_cs_parameter
    response_error = False
    async with channel.typing():
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
                            content = str(response.content)
                        except UnicodeDecodeError:
                            await channel.send(
                                "*Cleverbot fatal error, please use " + bot_command_prefix_string + "clearclever")
                            return
    if response_error:  # an error occurred (JSON NOT CORRECT - USE THE CONTENT AS A STRING)
        start_pos = content.find("\"output\":\"") + 10
        end_pos = content.find("\"conversation_id\":") - 2
        if start_pos == -1 or end_pos == -1:
            print("Error calculating sub-string positions")
        else:
            reply = content[start_pos:start_pos + (end_pos - start_pos)]  # calculate cleverbot reply substring
            await channel.send(reply)
        clear_cleverbot_parameters()  # clear cleverbot to begin a new conversation
    else:  # normal cleverbot reply (json file)
        request_result_cs = content["cs"]
        print("Cleverbot interaction number:" + content["interaction_count"])
        if bot.cleverbot_cs_parameter != request_result_cs and int(
                content["interaction_count"]) > bot.cleverbot_reply_number:
            bot.cleverbot_reply_number = int(content["interaction_count"])
            bot.cleverbot_cs_parameter = request_result_cs
        await channel.send(content["output"])


# Function that check if a command exist in bot commands (return True if exist, False otherwise)
def __check_command_exist(message: discord.message):
    command = (message.content.strip()[1:]).lower()
    for bot_command in bot.commands:
        if command.startswith(bot_command.name.lower()):
            # command found
            return True
    # command doesn't exist
    return False


# ---------------------------------------------------------------------
# bot "on_message" event, called when a message is created and sent to a server.


@bot.event
async def on_message(message: discord.message):
    if message.author.bot:  # nothing to do, the message is from me
        return
    # ---------------------------------------------------------------------
    if await first_chat_alert(message.channel, message.author):
        print("first_chat_alert return true for " + str(message.author.name))
        return
    # ---------------------------------------------------------------------
    # get bot mention
    if message.guild is None:
        mention = bot.user.mention
    else:
        mention = message.guild.me.mention
    if len(message.mentions) >= 1:  # message starts with a mention, check if it's mine
        alternative_mention = mention[:2] + '!' + mention[2:]
        if message.content.startswith(mention) or message.content.startswith(
                alternative_mention):  # yes the message starts with a mention, it's me?
            if not message.content.startswith(mention):
                print("mention replaced with alternative_mention")
                mention = alternative_mention
            new_message = message.content.replace(str(mention), "",
                                                  1)  # remove the mention from the message (only 1)
            for found_mention in message.mentions:  # convert all mentions to names to make the message clear
                new_message = new_message.replace(str(found_mention.mention), str(found_mention.name))
            # ---------------------------------------------------------------------
            if getattr(bot, 'maintenanceMode') and not BotMethods.is_owner(
                    message.author):  # if it's in maintenance Mode
                return
            new_message = new_message.strip()  # remove additional spaces from cleverbot question (before and after)
            print("Cleverbot Question received, asking cleverbot...")
            await cleverbot_request(message.channel, new_message)
            print("-------------------------")
        else:  # the message don't start with a mention, maybe it's a command?
            if getattr(bot, 'maintenanceMode') and not BotMethods.is_owner(
                    message.author):  # if it's in maintenance Mode then quit
                return
            command_exist = __check_command_exist(message)
            if message.content.startswith(bot_command_prefix_string) and command_exist:
                # if starts with command-prefix then process as command
                await bot.process_commands(message)  # tell the bot to try to execute the command
            elif message.guild is None:  # forward the message (if active)
                await forwards_message(message)
    else:
        if message.content.find("\\") == -1:  # error check for special chars
            if getattr(bot, 'maintenanceMode') and not BotMethods.is_owner(
                    message.author):  # if it's in maintenance Mode then quit
                return
            command_exist = __check_command_exist(message)
            if message.content.startswith(bot_command_prefix_string) and command_exist:
                # if starts with command-prefix then process as command
                await bot.process_commands(message)  # tell the bot to try to execute the command
            elif message.guild is None:  # forward the message (if active)
                await forwards_message(message)


# ---------------------------------------------------------------------


@bot.command()
async def hello(ctx: discord.ext.commands.Context):
    """Hello command - simple command for testing"""
    await ctx.message.channel.send("Hello " + ctx.message.author.name + "!")


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


@bot.command(hidden=True)
async def clearclever(ctx: discord.ext.commands.Context):
    """Clean Cleverbot Conversation"""
    print("-------------------------")
    print("Cleaning...")
    if clear_cleverbot_parameters():
        await ctx.message.channel.send("*Cleaning Complete*")
    else:
        print("Can't clean cleverbot chat")
    print("End of cleaning")
    print("-------------------------")


# ---------------------------------------------------------------------
# bot "on_ready" event, called when the client is done preparing the data received from Discord


@bot.event
async def on_ready():
    print("------------------------")
    print('[BOT on_ready()]:Logged as:' + bot.user.name + " ID:" + str(bot.user.id))
    # ----------
    await download_and_set_first_status()
    # ----------
    print("[BOT on_ready()]:Bot on_ready() ended, bot running")
    print("------------------------")


# ---------------------------------------------------------------------
# bot "on_reaction_add" event, called when a message has a reaction added to it


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if user != bot.user:  # if is not me
        print("------------------------")
        if isinstance(reaction.emoji, str):
            print("Adding my reaction to the message... (Emoji: " + reaction.emoji + ")")
        else:
            if isinstance(reaction.emoji, discord.Emoji) or isinstance(reaction.emoji, discord.PartialEmoji):
                print("Adding my reaction to the message... (Emoji Object: " + reaction.emoji.name + ")")
            else:
                print("UNKNOWN EMOJI OBJECT, ABORTING ADDING REACTION")
                return
        try:  # try adding my reaction
            await reaction.message.add_reaction(reaction.emoji)
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
    print("------------------------")
    print("---STARTING BOT EXECUTION, VERSION:" + str(botVariables.get_version()) + " BUILD:" + str(
        botVariables.get_build()) + "---")
    if botVariables.get_bot_distribution():
        print("---EXECUTING BOT USING THE BETA TOKEN---")
    else:
        print("---EXECUTING BOT USING THE NON-BETA TOKEN---")
    print("------------------------")
    pre_extension_attributes_initialization()
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
            quit(1)
        print("LOADING COMPLETED-->" + extension)
        print("------------------------")
    after_extension_attributes_initialization(botVariables.get_default_status())
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
