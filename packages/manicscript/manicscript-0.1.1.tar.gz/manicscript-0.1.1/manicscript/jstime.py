# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load timestamp methods
from datetime import datetime
from time import mktime

def datetime2epoch(dt):
        """Convert a datetime object into milliseconds from epoch"""
        return int(mktime(dt.timetuple())*1000)

def epoch2datetime(t):
        """Convert milliseconds from epoch to a local datetime object"""
        return datetime.fromtimestamp(t/1000.0)
