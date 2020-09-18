import requests
import json
from functools import lru_cache


class NoMatchingGames(Exception):
    pass


class NoMatchingEntity(Exception):
    pass


class ApiError(Exception):
    pass


class EntityData(object):
    """
    Use the blaseball.com API to turn an entity ID into a name
    """
    TEAM_ENDPOINT = "https://www.blaseball.com/database/team?ids="
    PLAYER_ENDPOINT = "https://www.blaseball.com/database/players?ids="

    @classmethod
    @lru_cache(maxsize=64)
    def get_team_name_by_id(cls, team_id, long_name=False):
        url = cls.TEAM_ENDPOINT + team_id
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ApiError()
        try:
            team_full = resp.json()
        except json.JSONDecodeError:
            raise NoMatchingEntity()
        else:
            return team_full['nickname']

    @classmethod
    @lru_cache(maxsize=64)
    def get_player_name_by_id(cls, player_id):
        url = cls.PLAYER_ENDPOINT + player_id
        resp = requests.get(url)
        if resp.status_code != 200:
            #raise ApiError()
            return None
        try:
            player_full = resp.json()
        except json.JSONDecodeError:
            raise NoMatchingEntity()
        else:
            return player_full[0]['name']


class RawGameData(object):
    """
    This class takes a game ID as an input, fetches the
    raw game outcome JSON from the blaseball-reference.com
    API, and wraps it so other classes can use it.
    """
    ENDPOINT = "https://www.blaseball.com/database/gameById/"

    def __init__(self, game_id):
        url = self.ENDPOINT + game_id
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ApiError()
        try:
            game_full = resp.json()
        except json.JSONDecodeError:
            raise NoMatchingGames()

        # Here is the list of useful keys from the
        # raw game data json returned:
        useful_keys = """
        id
        awayTeamName
        awayTeamNickname
        awayTeamEmoji
        awayPitcherName
        awayScore
        homeTeamName
        homeTeamNickname
        homeTeamEmoji
        homePitcherName
        homeScore
        season
        day
        isPostseason
        seriesIndex
        seriesLength
        shame
        weather""".split()
        useful_keys = [j.strip() for j in useful_keys]
        self.game = {}
        for k in useful_keys:
            self.game[k] = game_full[k]


class RawEventData(object):
    """
    This class takes a game ID as an input, fetches the
    raw event JSON from the blaseball-reference.com API,
    and wraps it so other classes can use it.

    Raw event data is a list of JSON events, 1 event = 1 AB.
    """
    ENDPOINT = "https://api.blaseball-reference.com/v1/events?gameId="
    def __init__(self, game_id):
        url = self.ENDPOINT + game_id
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ApiError()
        try:
            self.events_json = resp.json()
        except JSONDecodeError:
            raise NoMatchingGames()
        if len(self.events_json)==0:
            raise NoMatchingGames()

    def event_count(self):
        return self.events_json['count']

    def events(self):
        for event in self.events_json['results']:
            yield event

