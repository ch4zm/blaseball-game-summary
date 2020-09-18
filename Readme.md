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

* [Screenshots](#screenshots)
* [Installation](#installation)
    * [pip](#pip)
    * [source](#source)
* [Quick Start](#quick-start)
    * [Command line flags](#command-line-flags)
* [Data](#data)
* [Future work](#future-work)
* [Libraries used](#libraries-used)

## Screenshots

The `streak-finder` tool can print plain text tables to the console,
or output tables in HTML or Markdown format. Here are a few examples:

Look for winning streaks from the Tigers from Season 3 and 4,

![Winning streaks for Tigers Seasons 3 and 4](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/s34tigers.png)

Compare to winning streaks by the Pies at the same:

![Winning streaks for Tigers and Pies Seasons 3 and 4](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/s34tigerspies.png)

Show the top winning streaks in Season 1 for the Good League:

![Winning streaks for Good League Season 1](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/goodleaguestreaks.png)

Compare to top winning streaks in Season 1 for the Evil League:

![Winning streaks for Evil League Season 1](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/evilleaguestreaks.png)

Show game-by-game summaries of the worst losing streaks in blaseball history:

![Worst losing streaks](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/worstdetailsnew.png)

This tool also works on antique hardware!

![Worst losing streaks antique hardware](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/worstdetailsold.png)

The tool also offers the ability to export tables in HTML format,
in both short and long versions:

![HTML short command](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/htmlshort.png)

![HTML short page](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/htmlshortpage.png)

![HTML long command](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/htmllong.png)

![HTML long page](https://github.com/ch4zm/blaseball-streak-finder/raw/master/img/htmllongpage.png)

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


## Future work

* Writing other scripts that wrap this script, to store events
  for a given team over a given season, and analyze various


## Libraries used

This command line tool uses the following libraries under the hood:

* [configarparse](https://github.com/bw2/ConfigArgParse) for handling CLI arguments
* [requests](https://requests.readthedocs.io/en/master/) for making API request
