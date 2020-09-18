import requests
from .data_raw import RawGameData, RawEventData
from .parser import EventParser


"""
The heart of the game summary library is the 
JSON data structure that stores game summary data.
See docstring in parser.py for structure.

The GameSummaryData class defined here creates the 
raw event data class and the event parser, and hooks
them together.

The EventParser class is fed raw events for a given game 
and assembles the final game summary JSON.

The GameSummaryData wraps this JSON data for the View 
class to use.
"""


class GameSummaryData(object):
    """
    This class wraps the raw event data class
    and parses each event with an EventParser.

    When the EventParser has parsed all events,
    it can then generate a game summary JSON.

    """
    def __init__(self, game_id):
        # fetch raw game data
        raw = RawEventData(game_id)
        game = RawGameData(game_id)
        self.parser = EventParser(game)
        for i, event in enumerate(raw.events()):
            self.parser.parse(event)
        self.parser.finalize()

    def get_json(self):
        return self.parser.get_json()
