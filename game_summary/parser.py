import re
import json
from .data_raw import EntityData
from .util import get_stadium, TieGameException, GameParsingError


"""
Sample game summary json structure:

info:
- season: _
- day: _
- homeTeamNickname: _
- awayTeamNickname:
- stadium: _
- weather: _

boxscore:
- home: [0, 2, 0]
- away: [1, 2, 0]

linescore:
- home: [0,0,0,0,0,0,0,0,0]
- away: [0,0,0,0,0,0,0,0,1]

gameSummary:
- fielding:
  - DP: int
  - TP: int
- batting:
  - H: [0, 0, 0, 0, 0, 0, 0, 0, 0]
  - 1B:
    - player_name: count
  - 2B:
    - player_name: count
  - 3B
    - player_name: count
  - HR
    - player_name: count
  - BB
    - player_name: count
  - K
    - player_name: count
  - SAC
    - player_name: count
  - GDP
    - player_name: count
  - LOB: int
  - RBI: int
- baserunning:
  - SB
    - player_name: count
  - CS
    - player_name: count
- pitching
  - WP: _
  - WP-K: [0, 0, 0, 0, 0, 0, 0, 0, 0]
  - WP-BB: [0, 0, 0, 0, 0, 0, 0, 0, 0]
  - LP: _
  - LP-K: [0, 0, 0, 0, 0, 0, 0, 0, 0]
  - LP-BB: [0, 0, 0, 0, 0, 0, 0, 0, 0]
- weatherEvents:
  - "X was incinerated"
  - "The blooddrain gurgled"
  - "Y had an allergic reaction"
"""


class EventParser(object):
    """
    A class to parse a game event-by-event and keep track of the
    final cumulative quantities that will go into the game summary.
    """
    # Plain English names for weather codes
    WEATHER = {
        '0': 'Void',
        '1': 'Sunny',
        '2': 'Overcast',
        '3': 'Rainy',
        '4': 'Sandstorm',
        '5': 'Snowy',
        '6': 'Acidic',
        '7': 'Solar Eclipse',
        '8': 'Glitter',
        '9': 'Bloddrain',
        '10': 'Peanuts',
        '11': 'Lots of Birds',
        '12': 'Feedback',
        '13': 'Reverb'
    }
    # Names of event types that indicate a hit
    HIT_TYPES = ['SINGLE', 'DOUBLE', 'TRIPLE', 'HOME_RUN']
    # Words in the event text that indicate a weather event (lowercase)
    EVENT_TEXT = ['blooddrain', 'incinerate', 'feedback', 'allergic', 'yummy']
    # This is the final game summary JSON that we will return
    game_summary_data = {}
    # Keep track of runners during an inning
    n_baserunners = 0
    # Keep track of who won (to translate home/away to winner/loser)
    who_won = None

    def __init__(self, raw_game_data):
        # Store the raw game data JSON from blaseball.com
        self.game_data = raw_game_data

        # Populate game information for the summary header
        self.populate_game_info()

        # Prepare data structures for parsing
        self.init_box_score()
        self.init_line_score()
        self.init_game_summary()
        self.init_weather_events()

        # Have we seen any events in this half-inning yet
        self.not_leadoff = [[False,]*9, [False]*9]
        # Keep track of whether this is the inning leadoff batter
        self.leadoff = False

    def get_json(self):
        """Return the final game summary JSON"""
        return self.game_summary_data

    def populate_game_info(self):
        """
        Populate game info field of the final json that we are returning.
        This is used to create the header of the game summary:

        Season 4, Day 20
        Hellmouth Sunbeams @ Mexico City Wild Wings
        The Bucket, Mexico City
        Weather: Peanuts
        """
        # For a list of keys, see docstring in data_raw.py
        if self.game_data.game['homeScore'] > self.game_data.game['awayScore']:
            self.who_won = 'home'
        elif self.game_data.game['homeScore'] < self.game_data.game['awayScore']:
            self.who_won = 'away'
        else:
            self.who_won = 'tie'
            # Not dealing with this right now, only 6 games whose data was lost anyway?
            raise TieGameException()
        self.game_summary_data['info'] = dict(
            season = self.game_data.game['season']+1,
            day = self.game_data.game['day']+1,
            homeTeamNickname = self.game_data.game['homeTeamNickname'],
            awayTeamNickname = self.game_data.game['awayTeamNickname'],
            homeTeamName = self.game_data.game['homeTeamName'],
            awayTeamName = self.game_data.game['awayTeamName'],
            stadium = get_stadium(self.game_data.game['homeTeamNickname']),
            weather = self.WEATHER[str(self.game_data.game['weather'])]
        )

    def init_box_score(self):
        """
        Initialize the lists holding the box score, which consists of 3 columns:
        Runs, Hits, Errors, and Weather Events

        home = [X, Y, Z]
        away = [A, B, C]
        """
        self.box_score = dict(
            home = [0, 0, 0],
            away = [0, 0, 0]
        )

    def init_line_score(self):
        """
        Initialize the lists holding the line score, which consists of two rows,
        one for each team, and an entry in each row for each inning. These are
        usually 9 x 2, but for extra innings they can grow to N x 2.
        We initialize as 9-element lists, append as you go for extra innings
        """
        self.line_score = dict(
            home = [0,]*9,
            away = [0,]*9
        )

    def init_game_summary(self):
        """
        Keep track of fielding, batting, and baserunning for the home and away teams
        using a nested dictionary structure. See top docstring for schema.

        Each stat finally maps to a dictionary, where the key is the player name,
        and the value is the count
        """
        self.game_summary = {}
        for who in ['home', 'away']:
            self.game_summary[who] = {
                'fielding': {
                    'DP': 0,
                    'TP': 0
                },
                'batting': {
                    'H': [0,]*9,
                    '1B': {},
                    '2B': {},
                    '3B': {},
                    'HR': {},
                    'K': {},
                    'BB': {},
                    'SAC': {},
                    'GDP': {},
                    'GTP': {},
                    'LOB': 0,
                    'RBI': 0
                },
                'baserunning': {
                    'SB': {},
                    'CS': {}
                },
                'pitching': {
                    'K': [0,]*9,
                    'BB': [0,]*9,
                    'HBP': [0,]*9,
                }
            }

    def init_weather_events(self):
        self.weather_events = []

    def parse(self, event):
        self.update_leadoff(event)
        self.update_runner_count(event)
        self.parse_box_score(event)
        self.parse_line_score(event)
        self.parse_game_summary(event)
        self.parse_weather_events(event)

    def finalize(self):
        self.game_summary_data['box_score'] = self.box_score
        self.game_summary_data['line_score'] = self.line_score
        self.finalize_game_summary_pitching()
        self.game_summary_data['pitching_summary'] = self.pitching_summary
        self.game_summary_data['game_summary'] = self.game_summary
        self.game_summary_data['weather_events'] = self.weather_events

    def finalize_game_summary_pitching(self):
        # Remove pitching from game_summary and make it its own section
        hps, aps = self.game_summary['home'].pop('pitching'), self.game_summary['away'].pop('pitching')
        self.pitching_summary = {}
        # Switch from home/away to winner/loser
        if self.who_won=='home':
            winnerps = hps
            loserps = aps
        elif self.who_won=='away':
            winnerps = aps
            loserps = hps
        else:
            raise TieGameException()

        for oldkey in winnerps.keys():
            newkey = "WP-" + oldkey
            self.pitching_summary[newkey] = winnerps[oldkey]
        for oldkey in loserps.keys():
            newkey = "LP-" + oldkey
            self.pitching_summary[newkey] = loserps[oldkey]

        if self.who_won=='home':
            self.pitching_summary['WP'] = self.game_data.game['homePitcherName']
            self.pitching_summary['LP'] = self.game_data.game['awayPitcherName']
        elif self.who_won=='away':
            self.pitching_summary['WP'] = self.game_data.game['awayPitcherName']
            self.pitching_summary['LP'] = self.game_data.game['homePitcherName']
        else:
            raise TieGameException()

    def update_leadoff(self, event):
        self.leadoff = event['is_leadoff']
        inning = event['inning']
        top = event['top_of_inning']
        top_ix = 0 if top else 1

        # Can't trust the leadoff boolean... Some games are off
        try:
            if self.not_leadoff[top_ix][inning] is False:
                self.leadoff = True
                self.not_leadoff[top_ix][inning] = True
        except IndexError:
            # This is an extra-inning leadoff
            self.leadoff = True
            self.not_leadoff[top_ix] += [True]

        # Update leadoff
        try:
            self.not_leadoff[top_ix][inning] = True
        except IndexError:
            raise GameParsingError()

    def update_runner_count(self, event):
        # If top of inning, reset baserunner count
        if self.leadoff:
            self.n_baserunners = 0

        # If batter gets 1-3 bases, we have 1 more baserunner
        # (minus runs batted in)
        if event['bases_hit']>0 and event['bases_hit']<3:
            self.n_baserunners += 1
            self.n_baserunners -= event['runs_batted_in']

    def parse_box_score(self, event):
        # Check for runs
        rbi = False
        for event_text in event['event_text']:
            if 'score' in event_text.lower():
                rbi = True
        rbi = rbi or event['runs_batted_in'] > 0
        if rbi > 0:
            if event['top_of_inning']:
                label = 'away'
            else:
                label = 'home'
            # Increment runs by number of RBIs
            # (Note, this is simplistic and may count e.g. people walked home as a "run batted in")
            temp = self.box_score[label]
            temp[0] += max(1, event['runs_batted_in'])
            self.box_score[label] = temp

        # Check for hits
        if event['event_type'] in self.HIT_TYPES:
            if event['top_of_inning']:
                label = 'away'
            else:
                label = 'home'
            # Increment hits by 1
            temp = self.box_score[label]
            temp[1] += 1
            self.box_score[label] = temp

        # Check for errors
        if event['errors_on_play']:
            if event['top_of_inning']:
                label = 'home'
            else:
                label = 'away'
            temp = self.box_score[label]
            temp[2] += 1
            self.box_score[label] = temp

    def parse_line_score(self, event):
        # Update line score with new column if extra innings
        inning = event['inning']
        top = event['top_of_inning']
        top_ix = 0 if top else 1
        leadoff = self.leadoff

        # Extend inning-by-inning list if extra innings
        if inning>=9 and top and leadoff:
            self.line_score['home'] = self.line_score['home'] + [0]
            self.line_score['away'] = self.line_score['away'] + [0]

        # Update line score with new runs
        rbi = False
        for event_text in event['event_text']:
            if 'score' in event_text.lower():
                rbi = True
        rbi = rbi or event['runs_batted_in'] > 0
        if rbi:
            if event['top_of_inning']:
                label = 'away'
            else:
                label = 'home'
            # Increment runs in this inning by number of RBIs
            temp = self.line_score[label]
            temp[inning] += max(1, event['runs_batted_in'])
            self.line_score[label] = temp

    def parse_game_summary(self, event):
        self.parse_game_summary_fielding(event)
        self.parse_game_summary_batting(event)
        self.parse_game_summary_baserunning(event)
        self.parse_game_summary_pitching(event)

    def parse_game_summary_fielding(self, event):
        catkey = 'fielding'
        # Home team defends/pitches at top of inning
        if event['top_of_inning']:
            label = 'home'
        else:
            label = 'away'

        # Increment double plays
        if event['is_double_play']:
            self.game_summary[label][catkey]['DP'] += 1

        # Increment triple plays
        if event['is_triple_play']:
            self.game_summary[label][catkey]['TP'] += 1

    def parse_game_summary_batting(self, event):
        catkey = 'batting'
        if event['top_of_inning']:
            label = 'away'
        else:
            label = 'home'

        # Extend inning-by-inning list if extra innings
        inning = event['inning']
        top = event['top_of_inning']
        leadoff = self.leadoff
        if inning>=9 and top and leadoff:
            for ha in ['home', 'away']:
                self.game_summary[ha][catkey]['H'] += [0]

        # Class for looking up player/team IDs
        e = EntityData()

        event_key_map = {
            'SINGLE': '1B',
            'DOUBLE': '2B',
            'TRIPLE': '3B',
            'HOME_RUN': 'HR',
            'STRIKEOUT': 'K',
            'WALK': 'BB',
            'SACRIFICE': 'SAC'
        }
        if event['event_type'] in event_key_map:
            k = event_key_map[event['event_type']]
            # Look up player name
            batter_id = event['batter_id']
            batter_name = e.get_player_name_by_id(batter_id)
            # Increment this batter's count
            temp = self.game_summary[label][catkey][k]
            if batter_name not in temp.keys():
                temp[batter_name] = 1
            else:
                temp[batter_name] += 1
            self.game_summary[label][catkey][k] = temp

            if event['event_type'] in self.HIT_TYPES:
                temp = self.game_summary[label][catkey]['H']
                temp[inning] += 1
                self.game_summary[label][catkey]['H'] = temp

        # Handle GDP and GTP case
        if event['event_type']=='OUT':
            if event['is_double_play'] or event['is_triple_play']:
                # Look up player name
                batter_id = event['batter_id']
                batter_name = e.get_player_name_by_id(batter_id)
                if event['is_double_play']:
                    k = 'GDP'
                else:
                    k = 'GTP'
                # Increment this batter's GDP/GTP count
                temp = self.game_summary[label][catkey][k]
                if batter_name not in temp.keys():
                    temp[batter_name] = 1
                else:
                    temp[batter_name] += 1
                self.game_summary[label][catkey][k] = temp

        # If this is the third out, tabulate LOB
        if self._is_third_out(event):
            self.game_summary[label][catkey]['LOB'] += self.n_baserunners
            # n_baserunners will be reset at the top of the inning,
            # don't reset here b/c later methods will use it

        # Accumulate RBIs
        rbi = False
        for event_text in event['event_text']:
            if 'score' in event_text.lower():
                rbi = True
        rbi = rbi or event['runs_batted_in'] > 0
        if rbi:
            self.game_summary[label][catkey]['RBI'] += max(1, event['runs_batted_in'])


    def parse_game_summary_baserunning(self, event):
        catkey = 'baserunning'
        # Away is baserunning at top of inning
        if event['top_of_inning']:
            label = 'away'
        else:
            label = 'home'

        event_key_map = {
            'CAUGHT_STEALING': 'CS',
            'STOLEN_BASE': 'SB'
        }
        # Both CS and SB will require us to extract the
        # player name from the game event text, since
        # they only provide the batter's player id
        if event['event_type'] in event_key_map:
            k = event_key_map[event['event_type']]

            # We need to prepare the player name
            m = None
            if event['event_type']=='STOLEN_BASE':
                for event_text in event['event_text']:
                    m = re.search(r'^(.*) (stole|steals)', event_text)
                    if m is not None:
                        break
            if event['event_type']=='CAUGHT_STEALING':
                for event_text in event['event_text']:
                    m = re.search(r'^(.*) gets caught stealing', event_text)
                    if m is not None:
                        break

            if m is not None:
                player_name = m.group(1)
            else:
                print("\n".join(event['event_text']))
                player_name = "UNKNOWN"

            temp = self.game_summary[label][catkey][k]
            if player_name in temp:
                temp[player_name] += 1
            else:
                temp[player_name] = 1
            self.game_summary[label][catkey][k] = temp

    def parse_game_summary_pitching(self, event):
        catkey = 'pitching'
        # Home team defends/pitches at top of inning
        if event['top_of_inning']:
            label = 'home'
        else:
            label = 'away'

        # Extend inning-by-inning list if extra innings
        inning = event['inning']
        top = event['top_of_inning']
        leadoff = self.leadoff
        if inning>=9 and top and leadoff:
            for ha in ['home', 'away']:
                for stat in ['K', 'BB']:
                    self.game_summary[ha][catkey][stat] += [0]

        # Class for looking up player/team IDs
        e = EntityData()
        event_key_map = {
            'STRIKEOUT': 'K',
            'WALK': 'BB',
            'HIT_BY_PITCH': 'HBP'
        }
        if event['event_type'] in event_key_map:
            k = event_key_map[event['event_type']]
            temp = self.game_summary[label][catkey][k]
            temp[inning] += 1
            self.game_summary[label][catkey][k] = temp

    def parse_weather_events(self, event):
        # Check for weather events (?)
        for event_text in self.EVENT_TEXT:
            this_event = event['event_text']
            for event_line in this_event:
                if event_text in event_line:
                    self.weather_events.append(event_line)

    def _is_third_out(self, event):
        last1 = (event['outs_before_play']==2 and event['outs_on_play']==1)
        last2 = (event['outs_before_play']==1 and event['outs_on_play']==2)
        last3 = (event['outs_before_play']==0 and event['outs_on_play']==3)
        return last1 or last2 or last3
