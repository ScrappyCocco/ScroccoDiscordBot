# ---------------------------------------------------------------------
# IMPORTS

import re
import json
import aiohttp
import discord
import random

from botVariablesClass import BotVariables
from difflib import SequenceMatcher


# ---------------------------------------------------------------------


class BotMethods:
    """ Little class for static methods that i need to use multiple times in some classes """

    # ---------------------------------------------------------------------

    @staticmethod
    def cleanhtml(raw_html):
        """ Method that clean a string from html tags (used for !quote command)
            :param raw_html: The string to clean.
            :return: The clean string (without html tags)
        """
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    # ---------------------------------------------------------------------

    @staticmethod
    def is_owner(author):
        """ method that receives an author say if it's authorized for super-admin bot commands,
            read from BotVariables.owners
            :param author: The author to check.
            :return: return true is the author is authorized, If it is not then return false
        """
        ref = BotVariables()
        if str(author) in ref.get_owners_list():
            del ref
            return True
        else:
            del ref
            return False

    # ---------------------------------------------------------------------

    @staticmethod
    def is_server_admin(author):
        """ method that receives an author say if it's authorized for server-admin commands
            :param author: The author to check.
            :return: return true is the author is authorized, If it is not then return false
        """
        if isinstance(author, discord.Member):
            return author.top_role.permissions.administrator
        else:  # is not a server user
            return False

    # ---------------------------------------------------------------------

    @staticmethod
    def convert_hours_to_day(time_var: int):
        """ This function convert a time-format to another, is used to the weather api
            :param time_var: the day(0 to 19), is divided in 12h so 0 is today and 1 is today night, 2 is tomorrow....
            :return: return the day corresponding to the 12h-day format(0-19) to (0-9)
        """
        if time_var % 2 == 0:
            return int(time_var / 2)
        else:
            return int((time_var - 1) / 2)

    # ---------------------------------------------------------------------

    @staticmethod
    def platform_to_number(platform_name: str):
        """ This function is used for rocket league api: convert the platform name to his number
        :param platform_name: the platform name (steam, ps4 or xbox)
        :return: the number corresponding to the platform , -1 is the platform is not valid
        """
        platform = platform_name.lower()
        if platform == "steam":
            return 1
        if platform == "ps4" or platform == "ps":
            return 2
        if platform == "xbox" or platform == "xboxone":
            return 3
        return -1

    # ---------------------------------------------------------------------

    @staticmethod
    def similar(a, b, game_name_numbers):
        """ This function calculate how much the first string is similar to the second string
        :param a: First String
        :param b: Second String
        :param game_name_numbers: All the numbers in <a> string, used for an additional check
        :return: Return the similarity between the two string (0.0-1.0)
        """
        similarity = SequenceMatcher(None, a, b).ratio()
        if game_name_numbers is not None and len(game_name_numbers) > 0:  # additional check about numbers in the string
            number_found = False
            for character in b:  # check for every character
                if character.isdigit():  # if is a digit
                    for number_entry in game_name_numbers:  # compare it with numbers in the begin string
                        if str(number_entry) == str(character):
                            number_found = True
                            break
            if not number_found:  # number in the given string not in this one, reduce prob
                similarity -= 0.1
        return similarity

    # ---------------------------------------------------------------------

    @staticmethod
    async def get_player_minecraft_uuid(player_name: str):
        """ Download the minecraft uuid from a player name
        :param player_name: The name of the player to search
        :return: the player uuid or None if the player does not exist
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.mojang.com/users/profiles/minecraft/" + player_name) as resp:
                    r = await resp.json()
            uuid = r['id']  # getting the user MinecraftID
            print("get_player_minecraft_uuid: Minecraft ID Downloaded")
            return uuid
        except (json.decoder.JSONDecodeError, aiohttp.ContentTypeError):
            print("get_player_minecraft_uuid: Error getting PlayerID")
            return None

    # ---------------------------------------------------------------------

    @staticmethod
    def get_most_played_operator_index(operator_stats, is_atk: bool):
        """ Return the index of the most played operator in atk or in defense (Rainbow 6)
        :param operator_stats: the json with the operator stats
        :param is_atk: true if we are searching for ark operator, false otherwise
        :return: the json corresponding index of the most played operator
        """
        best_index = -1  # if it does not exist
        max_played = 0
        for i in range(0, len(operator_stats)):  # for each operator in the file
            if is_atk and str(operator_stats[i]['operator']['role']) == "atk":  # if i'm looking for atk and this is atk
                if operator_stats[i]['stats']['played'] > max_played:  # if has the max played time
                    max_played = operator_stats[i]['stats']['played']
                    best_index = i
            else:
                if not is_atk and str(
                        operator_stats[i]['operator']['role']) == "def":  # if i'm looking for def and this is def
                    if operator_stats[i]['stats']['played'] > max_played:  # if has the max played time
                        max_played = operator_stats[i]['stats']['played']
                        best_index = i
        return best_index  # return the best index

    # ---------------------------------------------------------------------

    @staticmethod
    def create_list_from_states_string(string_of_states: str):
        """ Return the list created from the string of possible statuses
        String format: "{Hello 1---Hello 2---I'm a bot}"
        :param string_of_states: string of possible statuses (format as described above)
        :return: ist of strings (used as possible statuses)
        """
        if string_of_states.startswith("{") and string_of_states.endswith("}"):
            return string_of_states[1:-1].split('---')
        else:
            return None

    # ---------------------------------------------------------------------

    @staticmethod
    def get_random_bot_state(list_of_states: list):
        """ Return a random state in the list of possible states
        :param list_of_states: list of possible bot in-game states
        :return: a random state from the list
        """
        return random.choice(list_of_states)

# ---------------------------------------------------------------------
