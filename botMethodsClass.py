# ---------------------------------------------------------------------
# IMPORTS

import re

from botVariablesClass import BotVariables

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
        ref = BotVariables(False)
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
        return author.top_role.permissions.administrator

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
            return int((time_var-1) / 2)

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

# ---------------------------------------------------------------------
