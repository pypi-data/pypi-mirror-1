# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load timestamp methods
from manicscript.jstime import datetime2epoch, epoch2datetime, datetime

class InvalidMessageDecode(Exception):
        """The message does not decode into a valid structure given the provided secret"""

class InvalidMessageEncode(Exception):
        """The message cannot be encoded into a JSON object"""

class InvalidMessageVerify(Exception):
        """The decoded message does not match the provided hash"""

class InvalidTicket(Exception):
        """The ticket is not valid for some reason"""

class InvalidTime(Exception):
        """The object validity period does not include the present"""

class ObjectNotYetValid(InvalidTime):
        """The object validity period has not begun"""

class ObjectExpired(InvalidTime):
        """The object validity period has passed"""

class NotAnAddressee(Exception):
        """The system/user is not an addressee of the given message"""
