import json
import os
import sys
from io import StringIO


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = os.path.abspath(os.path.join(root_path, 'data'))

SHORT2LONG_JSON = os.path.join(data_path, "short2long.json")
STADIUMS_JSON = os.path.join(data_path, "stadiums.json")

DALE_SAFE = "Dale" # for command line
DALE_UTF8 = "Dal\u00e9" # for display

FULL_DALE_SAFE = "Miami Dale" # for command line
FULL_DALE_UTF8 = "Miami Dal\u00e9" # for display


class TieGameException(Exception):
    pass


class GameParsingError(Exception):
    pass


def get_stadium(team_name):
    """Given a team name (long or short), get the name of the stadium"""
    team_name = sanitize_dale(team_name)
    result = None
    stadiums = get_stadiums()
    
    if team_name in stadiums.keys():
        # Easy case: we got a short name
        result = stadiums[team_name]
    elif team_name in stadiums.values():
        # Hard case: we were given a long name,
        # so get corresponding short name
        for k, v in stadium.items():
            if v==team_name:
                short_name = k
                break
        result = stadiums[short_name]
    else:
        raise Exception(f"Error: unrecognized team name: {team_name}")
    return result


def get_stadiums():
    stadiums = None
    if os.path.exists(STADIUMS_JSON):
        with open(STADIUMS_JSON, 'r') as f:
            stadiums = json.load(f)
    else:
        raise FileNotFoundError("Missing stadium names data file: %s"%(STADIUMS_JSON))
    return stadiums


def get_short2long():
    """Get the map of team nicknames to team full names"""
    short2long = None
    if os.path.exists(SHORT2LONG_JSON):
        with open(SHORT2LONG_JSON, 'r') as f:
            short2long = json.load(f)
    else:
        raise FileNotFoundError("Missing team nickname to full name data file: %s"%(SHORT2LONG_JSON))
    return short2long


def desanitize_dale(s):
    """Utility function to change sanitized Dale back to unicode"""
    if s == DALE_SAFE:
        return DALE_UTF8
    elif s == FULL_DALE_SAFE:
        return FULL_DALE_UTF8
    else:
        return s


def sanitize_dale(s):
    """Utility function to make CLI flag value easier to set"""
    if s == DALE_UTF8:
        return DALE_SAFE
    elif s== FULL_DALE_UTF8:
        return FULL_DALE_SAFE
    else:
        return s


class CaptureStdout(object):
    """
    A utility object that uses a context manager
    to capture stdout.
    """
    def __init__(self):
        # Boolean: should we pass everything through to stdout?
        # (this object is only functional if passthru is False)
        super().__init__()

    def __enter__(self):
        """
        Open a new context with this CaptureStdout
        object. This happens when we say
        "with CaptureStdout() as output:"
        """
        # We want to swap out sys.stdout with
        # a StringIO object that will save stdout.
        # 
        # Save the existing stdout object so we can
        # restore it when we're done
        self._stdout = sys.stdout
        # Now swap out stdout 
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        """
        Close the context and clean up.
        The *args are needed in case there is an
        exception (we don't deal with those here).
        """
        # Store the result we got
        self.value = self._stringio.getvalue()

        # Clean up (if this is missing, the garbage collector
        # will eventually take care of this...)
        del self._stringio

        # Clean up by setting sys.stdout back to what
        # it was before we opened up this context.
        sys.stdout = self._stdout

    def __repr__(self):
        """When this context manager is printed, it looks like the game ID string"""
        return self.value
