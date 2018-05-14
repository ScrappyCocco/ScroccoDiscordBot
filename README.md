# Scrocco Discord Bot
This is a little Python Bot i made for my Discord server and a couple of friends's Discord server.

## Getting Started

These instructions will get you a copy of the bot up and running on your local machine for development and testing purposes.
If you want the bot up 24/7 you should buy a Python Hosting service for the bot.

### Prerequisites

To running the bot you'll need Python (i used python-3.6.X) and to install all the packages in requirements.txt, you can install them with:

```
pip install -r requirements.txt
```

You need also **all** the API key you'll find in [bot_data_examples.json](bot_data_examples.json) (cleverbot, steam, ...),
so you must fill all the variables in "bot_data_examples.json" and **rename it** in "bot_data.json"
(a little documentation of the JSON file can be found in [botVariablesClass.py](botVariablesClass.py)).

**If you don't want a command**, you have to MANUALLY delete it, this is how: 
1. If the command use an api key, start removing the method that get it and its call in _full_startup_check()_ in the _botVariables_ class;
1. Now you have to remove the command, locate it and delete the whole command;
1. Repeat this for every command you don't want in the bot.

(If you remove the check from _botVariables_ but not the command you'll have runtime errors when someone use that command)

## Starting the bot

After you installed and configured everything you can try to run the main class (botMainClass.py) with the command:
```
py botMainClass.py
``` 
This will start the bot or show the errors you have to fix.

## Built Using

* [Danny - Discord.py](https://github.com/Rapptz/discord.py) - Discord Python API
* [SlashNephy - Hypixthon](https://github.com/SlashNephy/Hypixthon) - Hypixel API
* [smiley - steamapi](https://github.com/smiley/steamapi) - Steam API
* [More on [requirements.txt](requirements.txt)]

## Authors

* **ScrappyCocco** - *Initial work and updates*
* *Special thanks to all my friends for helping me testing this bot*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
