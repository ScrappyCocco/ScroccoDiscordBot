# ---------------------------------------------------------------------
# IMPORTS
# NOTHING TO IMPORT

# ---------------------------------------------------------------------


class BotVariables:
    cleverKey = "YourKey"
    hypixelKey = "YourKey"
    steamKey = "YourKey"

    version = "0.90"

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
    readStateUrl = "URL/readState.php"
    writeStateUrl = "URL/writeState.php"
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
    # -------------------------------------------------

    def __init__(self):
        print("CALLING MINI-CLASS-->" + self.__class__.__name__ + " class called")

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
