# ---------------------------------------------------------------------
# IMPORTS
# NOTHING TO IMPORT

# ---------------------------------------------------------------------


class BotVariables:
    cleverKey = "YourKey"  # https://www.cleverbot.com/api/
    hypixelKey = "YourKey"  # https://api.hypixel.net/
    steamKey = "YourKey"  # https://steamcommunity.com/dev/apikey
    gifKey = "YourKey"  # http://api.giphy.com/

    maxCleverbotRequests = 10  # max number of requests in case of errors

    version = "0.91"

    # maintenanceMode = False  # indicate if the bot is in maintenanceMode (only admins can use it)
    # maintenanceMode has moved as bot attr (useful because i can access the bot attrs from every class)
    # lastInGameStatus = ""
    # lastInGameStatus has moved as bot attr

    description = """Bot by ScrappyCocco!"""  # bot description
    commands_prefix = "!"

    owners = ["ScrappyCocco#4468"]  # discord username of who can admin the bot
    ownerPrivateMessagesID = "144488066998992896"  # discord id where private messages will be sent
    numbersEmoji = [":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]

    indexError = 0  # index used to count cleverbot errors

    startup_extensions = ["botGamingApi", "botMaintenanceCommands", "botCommonCommands"]
    # discord extensions to load on startup

    defaultStatus = "Branzini 4 Ever"

    # read and write url where i store the current in-game status to read it in case of reboot or update
    readStateUrl = "http://URL/readState.php"
    writeStateUrl = "http://URL/writeState.php"
    writeStateParamName = "GameString"  # the param name for the post request at writeStateUrl
    #  when i update the in-game status i make a post-request to "writeStateUrl" passing the new status in a
    #  param called "writeStateParamName" to save the status on server, from there i can read it making
    #  a simple request to "readStateUrl"

    memeGeneratorUsername = "yourUsername"
    memeGeneratorPassword = "yourPassword"
    # username and password of meme generator (https://api.imgflip.com/)

    discordFinalBotApiToken = "YourKey"
    discordBetaBotApiToken = "YourKey"
    # there are 2 api keys because i use the "beta" key before publishing the bot in his "final" version
    # you can create apps from https://discordapp.com/developers/applications/me

    emptyApiKey = "YourKey"
    # -------------------------------------------------

    def __init__(self):
        print("CALLING MINI-CLASS-->" + self.__class__.__name__ + " class called")
        if (
            self.cleverKey == self.emptyApiKey or
            self.hypixelKey == self.emptyApiKey or
            self.steamKey == self.emptyApiKey or
            self.gifKey == self.emptyApiKey or
            self.discordFinalBotApiToken == self.emptyApiKey or
            self.discordBetaBotApiToken == self.emptyApiKey or
            self.memeGeneratorUsername == "yourUsername" or
            self.memeGeneratorPassword == "yourPassword"
        ):
            print("FATAL ERROR -> SOME API KEY ARE MISSING - BOT WON'T WORK CORRECTLY")

    def __del__(self):
        print("DESTROYING MINI-CLASS-->" + self.__class__.__name__ + " class called")

    # -------------------------------------------------
    # GET METHODS FOR "CONST" VARS

    def get_clever_key(self):
        """Function that return the api key for the cleverbot api.
            :return: The Cleverbot API-KEY
        """
        return self.cleverKey

    def get_hypixel_key(self):
        """Function that return the api key for the hypixel api.
            :return: The Hypixel API-KEY
        """
        return self.hypixelKey

    def get_steam_key(self):
        """Function that return the api key for the stem api.
            :return: The Steam API-KEY
        """
        return self.steamKey

    def get_gif_key(self):
        """Function that return the api key for the gif api.
            :return: The Gif API-KEY
        """
        return self.gifKey

    def get_version(self):
        """Function that return the current version of the bot.
            :return: The current version of the bot
        """
        return self.version

    def get_discord_bot_token(self, isbeta: bool):
        """Return the token for the discord bot.
            :param isbeta: Specify if i need the bot beta token or the final token.
            :return: Required Discord token
        """
        if isbeta:
            return self.discordBetaBotApiToken
        else:
            return self.discordFinalBotApiToken


# ---------------------------------------------------------------------
