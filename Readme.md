# blaseball-game-summary

This repo contains a command line tool called `game-summary`
that creates a summary of the events in a game, formatted for
a variety of different formats.

The command line tool has only a few flags: a `-g/--game-id` flag,
to specify a game id (can be used repeatedly to print summaries of
multiple games), and a flag to indicate what format the output
should be in: `--markdown` for a markdown table format, `--text`
for a plain text format, `--rich` to format using rich text for the
console, and `--json` to dump a JSON object containing the info used
to make the game summary tables.


## Table of Contents

* [Example Output](#example-output)
* [Installation](#installation)
    * [pip](#pip)
    * [source](#source)
* [Quick Start](#quick-start)
    * [Command line flags](#command-line-flags)
* [Data](#data)
* [Future work](#future-work)
* [Libraries used](#libraries-used)

## Example Output

The `game-summary` tool can print summary tables of a game in multiple formats. Here are some examples.

We start by using the [`game-finder`](https://github.com/ch4zm/blaseball-game-finder) tool
to find a particular game's game ID.

Let's start with Season 4 Game 20. On this day the Sunbeams were at the Wild Wings, and Randy Marijuana
hit a dramatic two-run home run in the tenth inning for the Sunbeams, who went on to win the game. 

```
$ game-finder --season 4 --day 20 --team Sunbeams
25af923d-eab6-4dbf-9509-87376d9c6d0d
```

If we pass this to `game-summary`, we get the JSON version of the game summary, which is what the other
formats use under the hood:

```
$ game-finder --season 4 --day 20 --team Sunbeams | xargs game-summary
{
    "info": {
        "season": 4,
        "day": 20,
        "homeTeamNickname": "Wild Wings",
        "awayTeamNickname": "Sunbeams",
        "homeTeamName": "Mexico City Wild Wings",
        "awayTeamName": "Hellmouth Sunbeams",
        "stadium": "The Bucket, Mexico City",
        "weather": "Peanuts"
    },
    "box_score": {
        "home": [ 4, 9, 0 ],
        "away": [ 6, 12, 0 ]
    },
    "line_score": {
        "home": [ 0, 0, 1, 0, 3, 0, 0, 0, 0, 0 ],
        "away": [ 0, 0, 0, 0, 1, 3, 0, 0, 0, 2 ]
    },
    "pitching_summary": {
        "WP-K": [ 1, 0, 0, 1, 0, 0, 0, 0, 1, 0 ],
        "WP-BB": [ 0, 0, 0, 0, 0, 0, 0, 0, 1, 0 ],
        "WP-HBP": [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
        "LP-K": [ 1, 0, 1, 0, 1, 1, 0, 2, 2, 0 ],
        "LP-BB": [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
        "LP-HBP": [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
        "WP": "Miguel James",
        "LP": "Silvia Rugrat"
    },
    "game_summary": {
        "home": {
            "fielding": {
                "DP": 0,
                "TP": 0
            },
            "batting": {
                "H": [ 0, 0, 2, 1, 3, 0, 1, 0, 1, 1 ],
                "1B": {
                    "Jos\u00e9 Haley": 2,
                    "Yong Wright": 1,
                    "Ronan Combs": 3
                },
                "2B": {
                    "Cell Barajas": 1
                },
                "3B": {
                    "Summers Preston": 1
                },
                "HR": {
                    "Miguel Wheeler": 1
                },
                "K": {
                    "Summers Preston": 1,
                    "Sosa Hayes": 1,
                    "Cell Barajas": 1
                },
                "BB": {
                    "Axel Cardenas": 1
                },
                "SAC": {},
                "GDP": {},
                "GTP": {},
                "LOB": 6,
                "RBI": 4
            },
            "baserunning": {
                "SB": {},
                "CS": {}
            }
        },
        "away": {
            "fielding": {
                "DP": 0,
                "TP": 0
            },
            "batting": {
                "H": [ 1, 1, 1, 0, 1, 4, 0, 1, 1, 2 ],
                "1B": {
                    "Alaynabella Hollywood": 3,
                    "Alexander Horne": 1,
                    "Malik Romayne": 1,
                    "Emmett Internet": 1,
                    "Dudley Mueller": 1,
                    "Nerd Pacheco": 1
                },
                "2B": {
                    "Alexander Horne": 1
                },
                "3B": {},
                "HR": {
                    "Igneus Delacruz": 1,
                    "Alaynabella Hollywood": 1,
                    "Randall Marijuana": 1
                },
                "K": {
                    "Malik Romayne": 1,
                    "Nagomi Nava": 2,
                    "Nerd Pacheco": 1,
                    "Dudley Mueller": 1,
                    "Randall Marijuana": 1,
                    "Emmett Internet": 1,
                    "Alexander Horne": 1
                },
                "BB": {},
                "SAC": {},
                "GDP": {},
                "GTP": {},
                "LOB": 6,
                "RBI": 6
            },
            "baserunning": {
                "SB": {},
                "CS": {
                    "Igneus Delacruz": 1
                }
            }
        }
    },
    "weather_events": []
}
```

Now the text version of the same game:

```
$ game-finder --season 4 --day 20 --team Sunbeams | xargs game-summary --text

Game ID: 25af923d-eab6-4dbf-9509-87376d9c6d0d
Season 4 Day 20:
Hellmouth Sunbeams @ Mexico City Wild Wings
The Bucket, Mexico City
Weather: Peanuts


------------------------------------------
|                      |  R  |  H  |  E  |
------------------------------------------
| Sunbeams             |   6 |  12 |   0 |
------------------------------------------
| Wild Wings           |   4 |   9 |   0 |
------------------------------------------


------------------------------------------------------------------------------------------------------
|                      |   1 |   2 |   3 |   4 |   5 |   6 |   7 |   8 |   9 |     |  R  |  H  |  E  |
------------------------------------------------------------------------------------------------------
| Sunbeams             |   0 |   0 |   0 |   1 |   3 |   0 |   0 |   0 |   2 |     |   6 |  12 |   0 |
------------------------------------------------------------------------------------------------------
| Wild Wings           |   0 |   1 |   0 |   3 |   0 |   0 |   0 |   0 |   0 |     |   4 |   9 |   0 |
------------------------------------------------------------------------------------------------------



Pitching Summary:
-----------------

WP: Miguel James
WP-K: 3
WP-BB: 1
LP: Silvia Rugrat
LP-K: 8
LP-BB: 0



Team Summary: Sunbeams
----------------------
Batting:
HR: Igneus Delacruz (1), Alaynabella Hollywood (1), Randall Marijuana (1)
2B: Alexander Horne (1)
1B: Alaynabella Hollywood (3)
K: Nagomi Nava (2)
LOB: 6

Baserunning:
CS: Igneus Delacruz (1)


Team Summary: Wild Wings
------------------------
Batting:
HR: Miguel Wheeler (1)
3B: Summers Preston (1)
2B: Cell Barajas (1)
1B: Ronan Combs (3), José Haley (2)
LOB: 6
```

Likewise here is the rich text view:

```
$ game-finder --season 4 --day 20 --team Sunbeams | xargs game-summary --rich

Game ID: 25af923d-eab6-4dbf-9509-87376d9c6d0d
Season 4 Day 20:
Hellmouth Sunbeams @ Mexico City Wild Wings
The Bucket, Mexico City
Weather: Peanuts


┏━━━━━━━━━━━━┳━━━┳━━━━┳━━━┓
┃            ┃ R ┃ H  ┃ E ┃
┡━━━━━━━━━━━━╇━━━╇━━━━╇━━━┩
│ Sunbeams   │ 6 │ 12 │ 0 │
│ Wild Wings │ 4 │ 9  │ 0 │
└────────────┴───┴────┴───┘


┏━━━━━━━━━━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━━┳━━━┓
┃            ┃ 1 ┃ 2 ┃ 3 ┃ 4 ┃ 5 ┃ 6 ┃ 7 ┃ 8 ┃ 9 ┃   ┃ R ┃ H  ┃ E ┃
┡━━━━━━━━━━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━━╇━━━┩
│ Sunbeams   │ 0 │ 0 │ 0 │ 1 │ 3 │ 0 │ 0 │ 0 │ 2 │   │ 6 │ 12 │ 0 │
│ Wild Wings │ 0 │ 1 │ 0 │ 3 │ 0 │ 0 │ 0 │ 0 │ 0 │   │ 4 │ 9  │ 0 │
└────────────┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴────┴───┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pitching Summary:             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Winning Pitcher: Miguel James │
│ K: 3                          │
│ BB: 1                         │
│ Losing Pitcher: Silvia Rugrat │
│ K: 8                          │
│ BB: 0                         │
│                               │
└───────────────────────────────┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Team Summary: Sunbeams                                                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│                                                                           │
│ Batting:                                                                  │
│ HR: Igneus Delacruz (1), Alaynabella Hollywood (1), Randall Marijuana (1) │
│ 2B: Alexander Horne (1)                                                   │
│ 1B: Alaynabella Hollywood (3)                                             │
│ K: Nagomi Nava (2)                                                        │
│ LOB: 6                                                                    │
│                                                                           │
│ Baserunning:                                                              │
│ CS: Igneus Delacruz (1)                                                   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Team Summary: Wild Wings            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│                                     │
│ Batting:                            │
│ HR: Miguel Wheeler (1)              │
│ 3B: Summers Preston (1)             │
│ 2B: Cell Barajas (1)                │
│ 1B: Ronan Combs (3), José Haley (2) │
│ LOB: 6                              │
│                                     │
└─────────────────────────────────────┘

```

If there are weather events, there is a weather events box printed at the bottom. Here is the
Season 6 Day 84 Jazz Hands game against the Spies where Randall Marijuana was incinerated:

```
$ game-finder --season 6 --day 84 --team "Jazz Hands"
c8eb9f92-5f9e-444f-9ad4-e679a58a10bd
```

When we show the game summary, weather events (in this case, incineration) are collected at the bottom:

```
$ game-finder --season 6 --day 84 --team "Jazz Hands" | xargs game-summary --rich

Game ID: c8eb9f92-5f9e-444f-9ad4-e679a58a10bd
Season 6 Day 84:
Houston Spies @ Breckenridge Jazz Hands
The Pocket, Breckenridge
Weather: Solar Eclipse


┏━━━━━━━━━━━━┳━━━┳━━━┳━━━┓
┃            ┃ R ┃ H ┃ E ┃
┡━━━━━━━━━━━━╇━━━╇━━━╇━━━┩
│ Spies      │ 3 │ 6 │ 0 │
│ Jazz Hands │ 2 │ 7 │ 0 │
└────────────┴───┴───┴───┘


┏━━━━━━━━━━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┓
┃            ┃ 1 ┃ 2 ┃ 3 ┃ 4 ┃ 5 ┃ 6 ┃ 7 ┃ 8 ┃ 9 ┃   ┃ R ┃ H ┃ E ┃
┡━━━━━━━━━━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━╇━━━┩
│ Spies      │ 0 │ 0 │ 0 │ 1 │ 0 │ 0 │ 0 │ 0 │ 2 │   │ 3 │ 6 │ 0 │
│ Jazz Hands │ 2 │ 0 │ 0 │ 0 │ 0 │ 0 │ 0 │ 0 │ 0 │   │ 2 │ 7 │ 0 │
└────────────┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pitching Summary:               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Winning Pitcher: Math Velazquez │
│ K: 2                            │
│ BB: 3                           │
│ Losing Pitcher: Agan Harrison   │
│ K: 1                            │
│ BB: 4                           │
│                                 │
└─────────────────────────────────┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Team Summary: Spies           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Fielding:                     │
│ DP: 2                         │
│                               │
│ Batting:                      │
│ HR: Fitzgerald Blackburn (1)  │
│ 3B: Comfort Septemberish (1)  │
│ 1B: Reese Clark (2)           │
│ BB: Marco Escobar (2)         │
│ SAC: Fitzgerald Blackburn (1) │
│ LOB: 4                        │
│                               │
│ Baserunning:                  │
│ CS: Howell Franklin (1)       │
│                               │
└───────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Team Summary: Jazz Hands                        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│                                                 │
│ Batting:                                        │
│ HR: Kathy Mathews (1)                           │
│ BB: Aldon Cashmoney (2)                         │
│ GDP: Stephens Lightner (1), Nagomi Mcdaniel (1) │
│ LOB: 6                                          │
│                                                 │
└─────────────────────────────────────────────────┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Weather Events:                                                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Rogue Umpire incinerated Jazz Hands hitter Randall Marijuana! Replaced by    │
│ Steph Weeks                                                                  │
└──────────────────────────────────────────────────────────────────────────────┘

```


## Installation

### pip

```
pip install blaseball-game-summary
```

### source

Start by cloning the package:

```
git clone https://github.com/ch4zm/blaseball-game-summary
cd blaseball-game-summary
```

If installing from source, it is recommended you install the package
into a virtual environment. For example:

```
virtualenv vp
source vp/bin/activate
```

Now build and install the package:

```
python setup.py build
python setup.py install
```

Now test that the tool is available on the command line, and try out
a command to search for some streaks:

```
which game-summary
game-summary c8eb9f92-5f9e-444f-9ad4-e679a58a10bd
```

(this was the game that Randy Marijuana was incinerated from the Jazz Hands.)

## Quick Start

This tool is calling the `/events` API endpoint of the blaseball-reference.com
API, which returns a list of all events in a given game, and parsing through
each event to keep track of the box score, line score, pitching, batting, etc.

The tool stores the final game summary information in a JSON structure,
and each different output option (markdown, rich console text, or plain text)
utilizes the common JSON data structure.

### Command line flags

Command line flags are grouped into data options and view options.

Basic options:

* **Print version:** `--version` or `-v` flag

Positional arguments:

* **Game ID:** this is the first positional (non-flag) argument. Its value should be the UUID of a game.

View options:

* **Text:** Use the `--text` flag to output game summaries in plain text format

* **Rich:** Use the `--rich` flag to output game summaries in rich text format

* **Markdown:** Use the `--markdown` flag to output game summaries in Markdown format

* **JSON:** (default) Use the `--json` flag to output game summaries in JSON format

* **Box or Line Socre Only:** Add the `--box-only` flag to print the box score only
  (3-column table with Runs, Hits, and Errors); add the `--line-only` flag to print
  the line score only (multi-column table with one column per inning, plus the tally
  of Runs, Hits, and Errors at the end)

Using a configuration file:

* **Config file**: use the `-c` or `--config` file to point to a configuration file (see next section).


## Data

The data set used by this tool comes from `blaseball-reference.com`'s `/events` API endpoint.
The events endpoint returns an array of JSON objects, each one representing an at-bat in a
blaseball game. This program parses each event and extracts relevant information, accumulating
game summary information into a final JSON structure (see top of Readme for JSON structure).

The user can output the raw JSON (making game-summary a useful component in an analysis pipeline)
or it can format the JSON for viewing, in text, rich text, or markdown format.


## Future work

* Writing other scripts that wrap this script, to store events
  for a given team over a given season, and analyze various


## Libraries used

This command line tool uses the following libraries under the hood:

* [configarparse](https://github.com/bw2/ConfigArgParse) for handling CLI arguments
* [requests](https://requests.readthedocs.io/en/master/) for making API request
* [rich](https://github.com/willmcgugan/rich) for displaying rich text in the console
