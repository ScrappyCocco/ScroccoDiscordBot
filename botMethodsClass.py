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

# ---------------------------------------------------------------------
