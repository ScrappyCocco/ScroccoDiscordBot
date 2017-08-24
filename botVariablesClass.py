# ---------------------------------------------------------------------
# IMPORTS
import json

# ---------------------------------------------------------------------


class BotVariables:

    # ------------------------------------------------------
    # BOT JSON DOCUMENTATION
    # ------------------------------------------------------
    # JSON VARIABLES WITH EXPLANATION

    # API KEYS LIST
    # REMEMBER THAT if an api key is empty the bot won't start or the command won't work correctly
    # IF YOU don't want a command you have to MANUALLY remove the api key check (down here) and the command
    # cleverKey = "YourKey" : get yours from  https://www.cleverbot.com/api/
    # hypixelKey = "YourKey" : get yours from https://api.hypixel.net/
    # steamKey = "YourKey" : get yours from https://steamcommunity.com/dev/apikey
    # gifKey = "YourKey" : get yours from http://api.giphy.com/
    # weather key : get yours from http://api.wunderground.com/
    #   weather default_country must be in the "ISO 3166-1 alpha-2" format
    # rocket league stats api key : get yours from https://developers.rocketleaguestats.com
    #   rocket league default platform could be Steam, Ps4 OR XboxOne

    # maxCleverbotRequests : max number of requests to the cleverbot in case of errors (an error return an empty reply)

    # version and build : specify the bot version, you should NOT change those values if you don't edit the bot source

    # is_beta : specify if the bot have to use the beta api key or the final api key

    # description : bot simple description, write what you want in here

    # bot_icon : the url of the bot default icon (used only in some embed codes)

    # defaultStatus : the default bot IN-GAME status (if the bot can't download the last on startup, will use this state)

    # commands_prefix = "!" : the prefix of the commands (in this case !command)

    # open_source_link : bot source code page

    # private_chat_alert : the message the bot will send to users using the private chat with the bot for their first time

    # owners_list = ["ScrappyCocco#4468"] discord username of who can admin the bot
    # ownerPrivateMessagesID = "144488066998992896" discord id (in my case) where private messages will be sent, empty ( = "") if you want to deactivate it

    # startup_extensions = [...]
    # discord extensions to load on startup DO NOT touch that list if you don't edited the bot source code

    # read and write url where i store the current in-game status to read it in case of reboot or update
    # YOU CAN LEAVE THEM EMPTY, BOT WILL USE "defaultStatus" THAT YOU CAN CHANGE WITH !game, but on reboot it will use again "defaultStatus"
    # (remember that casual reboots happens in some hosting services)
    # readStateUrl = "http://URL/readState.php"
    # writeStateUrl = "http://URL/writeState.php"
    # writeStateParamName = "GameString" the param name for the POST request at writeStateUrl
    #   when i update the in-game status i make a post-request to "writeStateUrl" passing the new status in a
    #   param called "writeStateParamName" to save the status on server (do it as you want, up to you),
    #   from there i can read it (on bot startup) making a simple request to "readStateUrl"

    # memeGeneratorUsername = "yourUsername"
    # memeGeneratorPassword = "yourPassword"
    # username and password of meme generator (get yours from https://api.imgflip.com/)

    # discordFinalBotApiToken = "YourKey"
    # discordBetaBotApiToken = "YourKey"
    #   there are 2 api keys because i use the "beta" key before publishing the bot in his "final" version
    #   you can create apps from https://discordapp.com/developers/applications/me
    #   if you have (or want) only 1 api key, put that kay in BOTH discordFinalBotApiToken and discordBetaBotApiToken

    # ------------------------------------------------------
    # END BOT JSON DOCUMENTATION
    # ------------------------------------------------------

    bot_data_file = None
    file_name = "bot_data.json"
    privateChatUsers = []  # used to advise users that messages are sent to bot owner
    emptyApiKey = "YourKey"  # used to check if a key is empty
    emptyUrl = "http://URL/"
    numbersEmoji = [":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]
    indexError = 0  # index used to count cleverbot errors

    # -------------------------------------------------

    def __init__(self, should_check: bool):
        print("CALLING MINI-CLASS-->" + self.__class__.__name__ + " class called")
        try:
            with open(self.file_name) as data_file:
                self.bot_data_file = json.load(data_file)
        except FileNotFoundError:
            print("FATAL ERROR-->" + self.file_name + " FILE NOT FOUND, ABORTING...")
            quit(1)
        if should_check:
            self.full_startup_check()

    def __del__(self):
        print("DESTROYING MINI-CLASS-->" + self.__class__.__name__ + " class called")

    def full_startup_check(self):
        print("---STARTING FULL JSON CHECK---")
        self.get_clever_key()
        self.get_hypixel_key()
        self.get_gif_key()
        self.get_steam_key()
        self.get_meme_generator_username()
        self.get_meme_generator_password()
        self.get_owner_private_messages()
        self.get_owners_list()
        self.get_weather_key()
        self.get_rocket_league_key()
        self.get_discord_bot_token(False)
        print("---FULL JSON CHECK COMPLETED---")

    def check_empty_key(self, key):
        """Function that check the key for errors.
            :return: True if the key is ok, False if the Key is empty
        """
        if key == "" or key == self.emptyApiKey:
            print("ERROR, A KEY IS EMPTY - CHECK YOUR FILE")
            return False
        return True

    # -------------------------------------------------
    # GET METHODS FOR "CONST" VARS

    def get_clever_key(self):
        """Function that return the api key for the cleverbot api.
            :return: The Cleverbot API-KEY
        """
        key = self.bot_data_file["apiKeys"]["cleverbot"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE CLEVERBOT KEY (get yours from https://www.cleverbot.com/api/)- ABORTING")
            quit(1)

    def get_hypixel_key(self):
        """Function that return the api key for the hypixel api.
            :return: The Hypixel API-KEY
        """
        key = self.bot_data_file["apiKeys"]["hypixel"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE HYPIXEL KEY (get yours from https://api.hypixel.net/) - ABORTING")
            quit(1)

    def get_steam_key(self):
        """Function that return the api key for the stem api.
            :return: The Steam API-KEY
        """
        key = self.bot_data_file["apiKeys"]["steam"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE STEAM KEY (get yours from https://steamcommunity.com/dev/apikey) - ABORTING")
            quit(1)

    def get_gif_key(self):
        """Function that return the api key for the gif api.
            :return: The Gif API-KEY
        """
        key = self.bot_data_file["apiKeys"]["gif"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE GIF KEY (get yours from http://api.giphy.com/) - ABORTING")
            quit(1)

    def get_weather_key(self):
        """Function that return the api key for the weather api.
            :return: The Weather API-KEY
        """
        key = self.bot_data_file["weather"]["key"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE WEATHER KEY (get yours from http://api.wunderground.com/) - ABORTING")
            quit(1)

    def get_weather_country(self):
        """Function that return the default weather country to use
            :return: The default weather country
        """
        return self.bot_data_file["weather"]["default_country"]

    def get_rocket_league_key(self):
        """Function that return the api key for the rocket league stats api.
            :return: The rocket league stats API-KEY
        """
        key = self.bot_data_file["rocketleague"]["key"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE ROCKET LEAGUE KEY (get yours from https://developers.rocketleaguestats.com) - ABORTING")
            quit(1)

    def get_rocket_league_platform(self):
        """Function that return the default rocket league platform to use
            :return: The default rocket league api platform
        """
        return self.bot_data_file["rocketleague"]["default_platform"]

    def get_version(self):
        """Function that return the current version of the bot.
            :return: The current version of the bot
        """
        return self.bot_data_file["version"]

    def get_build(self):
        """Function that return the current build number of the bot.
            :return: The current build of the bot
        """
        return self.bot_data_file["build"]

    def get_description(self):
        """Function that return the description of the bot.
            :return: The description of the bot
        """
        return self.bot_data_file["description"]

    def get_bot_icon(self):
        """Function that return the current bot icon.
        This icon is used for embed messages
            :return: The current icon for the bot
        """
        return self.bot_data_file["bot_icon"]

    def get_default_status(self):
        """Function that return the current default status of the bot.
            :return: The current default status of the bot
        """
        return self.bot_data_file["defaultStatus"]

    def get_command_prefix(self):
        """Function that return the current command prefix of the bot.
            :return: The current command prefix of the bot
        """
        return self.bot_data_file["commands_prefix"]

    def get_open_source_link(self):
        """Function that return the bot source code link.
            :return: The bot source code link
        """
        return self.bot_data_file["open_source_link"]

    def get_private_chat_alert(self):
        """Function that return the bot private chat alert message
            :return: The bot private chat alert message
        """
        return self.bot_data_file["private_chat_alert"]

    def get_max_cleverbot_requests(self):
        """Function that return the max_cleverbot_requests.
            :return: The max_cleverbot_requests the bot can do (before an error for failed action)
        """
        return int(self.bot_data_file["maxCleverbotRequests"])

    def get_server_write_status_url(self):
        """Function that return the url where to write the status.
            :return: The url to send the new status (saving the status on the web)
        """
        return self.bot_data_file["server_state_saving"]["writeStateUrl"]

    def get_server_read_status_url(self):
        """Function that return the url where to read the status.
            :return: The url to read the last status (reading the status from the web)
        """
        return self.bot_data_file["server_state_saving"]["readStateUrl"]

    def get_server_write_status_parameter(self):
        """Function that return the POST param for the status
            :return: The POST param name for the status
        """
        return self.bot_data_file["server_state_saving"]["writeStateParamName"]

    def get_bot_distribution(self):
        """Function that return if the bot is in final or in beta version
            :return: True if it's in beta, false if it's in final version
        """
        key = self.bot_data_file["is_beta"]
        if key == "False":  # bot in final version
            return False
        if key == "True":  # bot in beta version
            return True
        print("BOT DISTRIBUTION ERROR - CHECK \"is_beta\" IN JSON AND PUT True or False")
        return True

    def get_meme_generator_username(self):
        """Function that return the username for the meme generator
            :return: The username for the meme generator
        """
        key = self.bot_data_file["meme_generator"]["username"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE MEME USERNAME (register on https://api.imgflip.com/) - BOT ABORTING")
            quit(1)

    def get_meme_generator_password(self):
        """Function that return the password for the meme generator
            :return: The password for the meme generator
        """
        key = self.bot_data_file["meme_generator"]["password"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE MEME PASSWORD (register on https://api.imgflip.com/) - BOT ABORTING")
            quit(1)

    def get_owner_private_messages(self):
        """Function that return the owner ID to send private messages
            :return: The owner ID to send private messages
        """
        owner_id = self.bot_data_file["owners_data"]["ownerPrivateMessagesID"]
        if owner_id == "":
            print("ERROR GETTING THE OWNER ID - EMPTY")
            return ""
        else:
            return owner_id

    def get_owners_list(self):
        """Function that return all the owners of the bot that have master permissions
            :return: All the owners of the bot that have master permissions
        """
        final_list = []
        for entry in self.bot_data_file["owners_data"]["owners_list"]:
            final_list.append(str(entry["name"]))
        if len(final_list) == 0:
            print("ERROR GETTING THE OWNERS LIST (i need at least 1 owner) - BOT ABORTING")
            quit(1)
        else:
            return final_list

    def get_startup_extensions(self):
        """Function that return the extensions to load on startup
            :return: The extensions to load on startup
        """
        final_list = []
        for entry in self.bot_data_file["startup_extensions"]:
            final_list.append(str(entry["name"]))
        return final_list

    def get_discord_bot_token(self, isbeta: bool):
        """Return the token for the discord bot.
            :param isbeta: Specify if i need the bot beta token or the final token.
            :return: Required Discord token
        """
        keybeta = self.bot_data_file["discord_tokens"]["discordBetaBotApiToken"]
        keyfinal = self.bot_data_file["discord_tokens"]["discordFinalBotApiToken"]
        if self.check_empty_key(keybeta) and self.check_empty_key(keyfinal):
            if isbeta:
                return keybeta
            else:
                return keyfinal
        else:
            print("ERROR GETTING THE DISCORD KEY (get yours from https://discordapp.com/developers/applications/me) - ABORTING")
            quit(1)


# ---------------------------------------------------------------------
