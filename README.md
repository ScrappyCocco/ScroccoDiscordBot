# Scrocco Discord Bot
This is a little Python Bot i made for my Discord server and a couple of friends's Discord server.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To running the bot you'll need Python (i used python-3.5.2) and to install all the packages in requirements.txt

```
pip install -r requirements.txt
```

You need also all the API key you'll find in "bot_data_examples.json" (cleverbot, steam, ...),
so you must fill all the variables in "bot_data_examples.json" and rename it in "bot_data.json"
(a little documentation of the JSON file can be found in [botVariablesClass.py](botVariablesClass.py)).

After you installed everything you can try to run the main class (botMainClass.py) with the command:
```
py botMainClass.py
``` 
This will start the bot or show the errors you have to fix.

## Built Using

* [SlashNephy - Hypixthon](https://github.com/SlashNephy/Hypixthon) - Hypixthon API
* [smiley - steamapi](https://github.com/smiley/steamapi) - Steam API
* [edwardslabs - cleverwrap.py](https://github.com/edwardslabs/cleverwrap.py) - Cleverbot Wrapper
* [More on [requirements.txt](requirements.txt)]

## Authors

* **ScrappyCocco** - *Initial work*
* *Special thanks to all my friends for helping me testing this bot*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
