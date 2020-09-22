import json
import os


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = os.path.abspath(os.path.join(root_path, 'data'))

SHORT2LONG_JSON = os.path.join(data_path, "short2long.json")
STADIUMS_JSON = os.path.join(data_path, "stadiums.json")


class TieGameException(Exception):
    pass


class GameParsingError(Exception):
    pass


def get_stadium(team_name):
    """Given a team name (long or short), get the name of the stadium"""
    result = None
    stadiums = get_stadiums()
    
    if team_name in stadiums.keys():
        # Easy case: we got a short name
        result = stadiums[team_name]
    elif team_name in stadium.values():
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
