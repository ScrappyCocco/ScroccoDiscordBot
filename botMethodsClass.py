# ---------------------------------------------------------------------
# IMPORTS

import re

from botVariablesClass import BotVariables

# ---------------------------------------------------------------------


class BotMethods:
    """ Little class for static (and non) methods that i need to use multiple times in some classes """
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

    @staticmethod
    def is_server_admin(author):
        """ method that receives an author say if it's authorized for admin commands,
            read from BotVariables.owners
            :param author: The author to check.
            :return: return true is the author is authorized, If it is not then return false
        """
        return author.top_role.permissions.administrator

    @staticmethod
    def convert_hours_to_day(time_var: int):
        """ This function convert a time-format to another, is used to the weather api
            :param time_var: the day(0 to 19), is divided in 12h so 0 is today and 1 is today night, 2 is tomorrow....
            :return: return the day corresponding to the 12h-day format(0-19) to (0-9)
        """
        if time_var == 0 or time_var == 1:
            return 0
        if time_var == 2 or time_var == 3:
            return 1
        if time_var == 4 or time_var == 5:
            return 2
        if time_var == 6 or time_var == 7:
            return 3
        if time_var == 8 or time_var == 9:
            return 4
        if time_var == 10 or time_var == 11:
            return 5
        if time_var == 12 or time_var == 13:
            return 6
        if time_var == 14 or time_var == 15:
            return 7
        if time_var == 16 or time_var == 17:
            return 8
        if time_var == 18 or time_var == 19:
            return 9

# ---------------------------------------------------------------------
