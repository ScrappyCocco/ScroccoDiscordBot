# ---------------------------------------------------------------------
# IMPORTS

import json


# ---------------------------------------------------------------------


class BotVariables:
    bot_data_file = None
    privateChatUsers = []  # used to advise users that messages are sent to bot owner
    emptyApiKey = "YourKey"  # used to check if a key is empty
    emptyUrl = "http://URL/"
    numbersEmoji = [":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]
    command_prefix = ""  # initialized after the check

    # -------------------------------------------------

    def __init__(self, should_check=False):
        print("CALLING MINI-CLASS-->" + self.__class__.__name__ + " class called")
        file_name = "bot_data.json"
        try:
            with open(file_name) as data_file:
                self.bot_data_file = json.load(data_file)
        except FileNotFoundError:
            print("FATAL ERROR-->" + file_name + " FILE NOT FOUND, ABORTING...")
            quit(1)
        if should_check:  # used because i do a full check only the first time the bot load
            self.full_startup_check()
        # After the full_startup_check, i know there are no problems
        self.command_prefix = self.get_command_prefix()

    def __del__(self):
        print("DESTROYING MINI-CLASS-->" + self.__class__.__name__ + " class called")

    def full_startup_check(self):
        print("---STARTING FULL JSON CHECK---")
        self.get_clever_key()
        self.get_hypixel_key()
        self.get_gif_key()
        self.get_google_shortener_key()
        self.get_mashape_metacritic_key()
        self.get_steam_key()
        if self.get_bot_save_state_to_file() and self.get_bot_save_state_to_server():
            print("ERROR, BOT CANNOT READ FROM A FILE AND FROM THE WEB, DOUBLE TRUE VALUE FOUND - CHECK YOUR JSON FILE")
            quit(1)
        self.get_meme_generator_username()
        self.get_meme_generator_password()
        self.get_owner_private_messages()
        self.get_owners_list()
        self.get_weather_key()
        self.get_rocket_league_key()
        self.get_youtube_api_key()
        self.get_discord_bot_token(False)
        print("---FULL JSON CHECK COMPLETED---")

    def check_empty_key(self, key):
        """Function that check the key for errors.
            :return: True if the key is ok, False if the Key is not valid
        """
        if key is None or key == "" or key == self.emptyApiKey:
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

    def get_google_shortener_key(self):
        """Function that return the api key for the google shortener api.
            :return: The google shortener API-KEY.
        """
        key = self.bot_data_file["apiKeys"]["google_shortener"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE GOOGLE SHORTENER KEY (check bot documentation) - ABORTING")
            quit(1)

    def get_mashape_metacritic_key(self):
        """Function that return the api key for the google shortener api.
            :return: The google shortener API-KEY.
        """
        key = self.bot_data_file["apiKeys"]["X-Mashape-Key"]
        if self.check_empty_key(key):
            return key
        else:
            print("ERROR GETTING THE MASHAPE API KEY FOR METACRITIC (check bot documentation) - ABORTING")
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
            print(
                "ERROR GETTING THE ROCKET LEAGUE KEY (get yours from https://developers.rocketleaguestats.com) - ABORTING")
            quit(1)

    def get_rocket_league_platform(self):
        """Function that return the default rocket league platform to use
            :return: The default rocket league api platform
        """
        return self.bot_data_file["rocketleague"]["default_platform"]

    def get_youtube_api_key(self):
        """Function that return the api key for the youtube api.
            :return: The youtube API-KEY
        """
        key = self.bot_data_file["youtube"]["key"]
        if self.check_empty_key(key):
            return key
        else:
            print(
                "ERROR GETTING THE YOUTUBE KEY (get yours from https://developers.google.com/youtube/v3/getting-started) - ABORTING")
            quit(1)

    def get_list_youtube_channels_check(self):
        """Function that return the list of the youtube channels to check, with all the details about the notification
        :return: The list of the youtube channels to check
        """
        return self.bot_data_file["youtube"]["channels"]

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

    def get_bot_save_state_to_file(self):
        """Function that return a boolean that indicate if the status must be saved on a text file
        Remember: the bot must have write permission on disk to create the file, otherwise you must create it
        :return: a boolean that indicate if the status must be saved on a text file
        """
        return self.bot_data_file["bot_status"]["save_to_file"]["save_state_to_file"]

    def get_bot_save_state_to_server(self):
        """Function that return a boolean that indicate if the status must be saved on a server sending a post request to a page
        (Is up to you to create that page)
        :return: a boolean that indicate if the status must be saved on a server
        """
        return self.bot_data_file["bot_status"]["server_state_saving"]["save_state_to_server"]

    def get_bot_save_state_file_name(self):
        """Function that return the name of the file to create or open to save or read the status
        :return: The name of the file to create or open
        """
        return self.bot_data_file["bot_status"]["save_to_file"]["file_name"]

    def get_bot_random_state_change_time(self):
        """Function that return the time to wait before randomize the bot in-game status again
        (Only if there's a list of possible statuses)
        :return: The time to wait before randomize the bot in-game status again (in seconds)
        """
        return self.bot_data_file["bot_status"]["random_status_change_interval"]

    def get_default_status(self):
        """Function that return the current default status of the bot.
            :return: The current default status of the bot
        """
        return self.bot_data_file["bot_status"]["defaultStatus"]

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
        return self.bot_data_file["bot_status"]["server_state_saving"]["writeStateUrl"]

    def get_server_read_status_url(self):
        """Function that return the url where to read the status.
            :return: The url to read the last status (reading the status from the web)
        """
        return self.bot_data_file["bot_status"]["server_state_saving"]["readStateUrl"]

    def get_server_write_status_parameter(self):
        """Function that return the POST param for the status
            :return: The POST param name for the status
        """
        return self.bot_data_file["bot_status"]["server_state_saving"]["writeStateParamName"]

    def get_bot_distribution(self):
        """Function that return if the bot is in final or in beta version
            :return: True if it's in beta, false if it's in final version
        """
        key = self.bot_data_file["is_beta"]
        if isinstance(key, bool):
            return key
        else:
            print("BOT DISTRIBUTION ERROR - CHECK \"is_beta\" IN JSON AND WRITE true or false")
            quit(1)

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
            print(
                "ERROR GETTING THE DISCORD KEY (get yours from https://discordapp.com/developers/applications/me) - ABORTING")
            quit(1)

# ---------------------------------------------------------------------
