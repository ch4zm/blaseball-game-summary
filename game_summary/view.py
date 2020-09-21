import sys
import json
from rich.console import Console
from rich.table import Table
from .util import TieGameException
from .data_model import GameSummaryData
from .data_raw import NoMatchingGames, ApiError


class BaseView(object):
    """
    The BaseView object provides base functionality for all Views.
    This class stores a set of game IDs, and displays game summary
    data for each one.

    For each game ID, this class:
    - creates an object to wrap the raw event data
    - creates an object to parse the raw data and create game summary data
    - displays the game summary data using subclass-specific method

    View classes. The View class creates a RawEventData class,
    gets the raw event data for the given game ID, and parses
    it for viewing. The parsing functions are common to all
    View classes.
    """
    def __init__(self, options):
        """
        Get all of the game summary data here.

        Game data is stored in a dictionary - key is game ID,
        value is the game summary JSON object.
        """
        self.game_id = options.game_id
        self.box_only = options.box_only
        self.line_only = options.line_only
        try:
            gsd = GameSummaryData(self.game_id)
            self.json_game_data = gsd.get_json()
        except NoMatchingGames as e:
            print(f"No matching games found for game id {self.game_id}. Try using blaseball-game-finder to look for game IDs.")
            sys.exit(1)
        except ApiError as e:
            print(f"Error reaching API for game id {self.game_id}, check log for details")
            sys.exit(1)
        except TieGameException as e:
            print(f"Error with game id {self.game_id}, that game ended in a tie")
            sys.exit(0)

class JsonView(BaseView):
    """
    The simplest view class, this passes the game summary JSON
    straight through to the user
    """
    def show(self):
        print(json.dumps(self.json_game_data, indent=4))


class TextView(BaseView):
    """
    Print a game summary in plain text format
    """
    def show(self):
        d = self.json_game_data

        # ---------------
        # game info
        print("")
        print("\n".join(self.text_info_header()))
        print("")

        # ---------------
        # box score
        if not self.line_only:
            print("")
            print("\n".join(self.text_box_score()))
            print("")

        # ---------------
        # line score
        if not self.box_only:
            print("")
            print("\n".join(self.text_line_score()))
            print("")

        # ---------------
        # pitching summary
        if not self.line_only and not self.box_only:
            print("")
            print("\n".join(self.text_pitching_summary()))
            print("")

        # ---------------
        # team summaries
        if not self.line_only and not self.box_only:
            print("")
            for who in ['away', 'home']:
                print("\n".join(self.text_team_summary(who)))
                print("")

        # ---------------
        # weather events
        if not self.line_only and not self.box_only:
            if len(d['weather_events'])>0:
                print("")
                print("\n".join(self.text_weather_events()))
                print("")

    def text_info_header(self):
        """
        d: dictionary, result of GameSummaryData.json() call
        """
        d = self.json_game_data
        info_header = []
        info_header.append("Game ID: %s"%(self.game_id))
        info_header.append("Season %d Day %d:"%(d['info']['season'], d['info']['day']))
        info_header.append("%s @ %s"%(
            d['info']['awayTeamName'],
            d['info']['homeTeamName'],
        ))
        info_header.append(d['info']['stadium'])
        info_header.append("Weather: %s"%(d['info']['weather']))
        return info_header

    def text_box_score(self):
        """Make a box score for a text view"""
        d = self.json_game_data
        box_score = []

        def _make_box_score_row_text(name, row):
            rowstr = ""
            rowstr += "| %-20s | "%(name)
            for i in range(3):
                rowstr += "%3d | "%(row[i])
            return rowstr

        def _make_box_header_row_text():
            header = "| %20s |  R  |  H  |  E  |"%(" ")
            return header

        box_score.append("-"*42)
        box_score.append(_make_box_header_row_text())
        box_score.append("-"*42)
        box_score.append(_make_box_score_row_text(d['info']['awayTeamNickname'], d['box_score']['away']))
        box_score.append("-"*42)
        box_score.append(_make_box_score_row_text(d['info']['homeTeamNickname'], d['box_score']['home']))
        box_score.append("-"*42)

        return box_score

    def text_line_score(self):
        """Make a line score for a text view"""
        d = self.json_game_data
        line_score = []

        def _make_line_score_row_text(name, line_row, box_row):
            rowstr = ""
            rowstr += "| %-20s | "%(name)
            for i in range(len(line_row)):
                rowstr += "%3d | "%(line_row[i])
            rowstr += "    | "
            for i in range(len(box_row)):
                rowstr += "%3d | "%(box_row[i])
            return rowstr

        def _make_line_header_row_text(line_row):
            header = ""
            header += "| %20s | "%(" ")
            for i in range(len(line_row)):
                header += "%3d | "%(i+1)
            header += "    | "
            header += " R  |  H  |  E  |"
            return header

        line_row = d['line_score']['away']
        box_row = d['box_score']['away']
        linelen = 2 + 23 + 6*len(line_row) + 4 + 1 + 6*len(box_row)

        line_score.append("-"*linelen)
        line_score.append(_make_line_header_row_text(line_row))
        line_score.append("-"*linelen)
        line_score.append(_make_line_score_row_text(d['info']['awayTeamNickname'], d['line_score']['away'], d['box_score']['away']))
        line_score.append("-"*linelen)
        line_score.append(_make_line_score_row_text(d['info']['homeTeamNickname'], d['line_score']['home'], d['box_score']['home']))
        line_score.append("-"*linelen)
        line_score.append("")

        return line_score

    def text_pitching_summary(self):
        """Make a pitching summary for the text view"""
        d = self.json_game_data
        pitching_summary = []

        ps = "Pitching Summary:"
        pitching_summary.append(ps)
        pitching_summary.append("-"*len(ps))
        pitching_summary.append("")
        for k in ['WP', 'WP-K', 'WP-BB']:
            pitching_summary.append("%s: %s"%(k, str(d['pitching_summary'][k])))
        for k in ['LP', 'LP-K', 'LP-BB']:
            pitching_summary.append("%s: %s"%(k, str(d['pitching_summary'][k])))
        pitching_summary.append("")

        return pitching_summary

    def text_team_summary(self, who):
        """Make a team summary for the text view"""
        d = self.json_game_data
        summ = d['game_summary'][who]
        team_summary = []

        ts = "Team Summary: %s"%(d['info']['%sTeamNickname'%(who)])
        team_summary.append(ts)
        team_summary.append("-"*len(ts))

        # Fielding summary
        if summ['fielding']['DP']>0 or summ['fielding']['TP']>0:
            team_summary.append("Fielding:")
            for k in ['DP', 'TP']:
                n = summ['fielding'][k]
                if n > 0:
                    team_summary.append("%s: %d"%(k, n))
            team_summary.append("")

        # Batting summary
        team_summary.append("Batting:")
        team_summary.append("RBI: %d"%(summ['batting']['RBI']))
        for k in ['HR', '3B', '2B', '1B', 'BB', 'K', 'SAC', 'GDP']:
            bmap = summ['batting'][k]
            if len(bmap.items())==0:
                continue
            # This string is the line to print for this stat
            line = "%s: "%(k)
            # Re-sort the map by value, highest to lowest
            newbmap = {k: v for k, v in sorted(bmap.items(), reverse=True, key=lambda item: item[1])}
            # Assemble BatterName (count) list
            to_add = []
            for player, value in newbmap.items():
                if (k=='1B' or k=='K' or k=='BB') and value<2:
                    continue
                to_add.append("%s (%d)"%(player, value))
            if len(to_add)>0:
                # Make it pretty and print
                line += ", ".join(to_add)
                team_summary.append(line)
        team_summary.append("LOB: %d"%(summ['batting']['LOB']))
        team_summary.append("")

        # Baserunning summary
        if len(summ['baserunning']['CS'])>0 or len(summ['baserunning']['SB'])>0:
            team_summary.append("Baserunning:")
            for k in ['SB', 'CS']:
                bmap = summ['baserunning'][k]
                if len(bmap.items())==0:
                    continue
                # This string is the line to print for this stat
                line = "%s: "%(k)
                # Re-sort the map by value, highest to lowest
                newbmap = {k: v for k, v in sorted(bmap.items(), reverse=True, key=lambda item: item[1])}
                # Assemble BatterName (count) list
                to_add = []
                for player, value in newbmap.items():
                    to_add.append("%s (%d)"%(player, value))
                if len(to_add)>0:
                    # Make it pretty and print
                    line += ", ".join(to_add)
                    team_summary.append(line)
            team_summary.append("")

        return team_summary

    def text_weather_events(self):
        d = self.json_game_data
        weather_summary = []

        we = "Weather Events:"
        weather_summary.append(we)
        weather_summary.append("-"*len(we))
        weather_summary.append("\n".join(d['weather_events']))
        weather_summary.append("")

        return weather_summary


class RichView(TextView):
    def show(self):
        d = self.json_game_data

        console = Console()

        # ---------------
        # game info
        console.print("")
        console.print("\n".join(self.text_info_header()))
        console.print("")

        # ---------------
        # box score
        if not self.line_only:
            console.print("")
            console.print(self.rich_box_score())
            console.print("")

        # ---------------
        # line score
        if not self.box_only:
            console.print("")
            console.print(self.rich_line_score())
            console.print("")

        # ---------------
        # pitching summary
        if not self.line_only and not self.box_only:
            console.print("")
            console.print(self.rich_pitching_summary())
            console.print("")

        # ---------------
        # team summaries
        if not self.line_only and not self.box_only:
            console.print("")
            for who in ['away', 'home']:
                console.print(self.rich_team_summary(who))
                console.print("")

        # ---------------
        # weather events
        if not self.line_only and not self.box_only:
            if len(d['weather_events'])>0:
                console.print("")
                console.print(self.rich_weather_events())
                console.print("")

    def rich_box_score(self):
        """Make a box score for a rich view"""
        d = self.json_game_data

        table = Table(show_header=True, header_style="bold")

        # Make table header row
        table.add_column(" ")
        table.add_column("R")
        table.add_column("H")
        table.add_column("E")

        # Away first, then home
        table.add_row(d['info']['awayTeamNickname'], *[str(j) for j in d['box_score']['away']])
        table.add_row(d['info']['homeTeamNickname'], *[str(j) for j in d['box_score']['home']])

        return table

    def rich_line_score(self):
        d = self.json_game_data

        table = Table(show_header=True, header_style="bold")

        table.add_column(" ")
        for i in range(len(d['line_score']['away'])):
            table.add_column(str(i+1))
        table.add_column(" ")
        table.add_column("R")
        table.add_column("H")
        table.add_column("E")

        table.add_row(
            d['info']['awayTeamNickname'],
            *[str(j) for j in d['line_score']['away']],
            " ",
            *[str(j) for j in d['box_score']['away']],
        )
        table.add_row(
            d['info']['homeTeamNickname'],
            *[str(j) for j in d['line_score']['home']],
            " ",
            *[str(j) for j in d['box_score']['home']],
        )

        return table

    def rich_pitching_summary(self):
        d = self.json_game_data

        table = Table(show_header=True, header_style="bold")

        ps = "Pitching Summary:"
        table.add_column(ps)

        table.add_row("[bold]Winning Pitcher:[/bold] %s"%(d['pitching_summary']['WP']))
        table.add_row("K: %d"%(d['pitching_summary']['WP-K']))
        table.add_row("BB: %d"%(d['pitching_summary']['WP-BB']))

        table.add_row("[bold]Losing Pitcher:[/bold] %s"%(d['pitching_summary']['LP']))
        table.add_row("K: %d"%(d['pitching_summary']['LP-K']))
        table.add_row("BB: %d"%(d['pitching_summary']['LP-BB']))

        table.add_row(" ")

        return table

    def rich_team_summary(self, who):
        d = self.json_game_data
        summ = d['game_summary'][who]

        table = Table(show_header=True, header_style="bold")

        ts = "Team Summary: %s"%(d['info']['%sTeamNickname'%(who)])
        table.add_column(ts)

        # Fielding summary
        if summ['fielding']['DP']>0 or summ['fielding']['TP']>0:
            table.add_row("[bold]Fielding:[/bold]")

            fielding_summary = []
            for k in ['DP', 'TP']:
                n = summ['fielding'][k]
                if n > 0:
                    fielding_summary.append("%s: %d"%(k, n))

            table.add_row("\n".join(fielding_summary))
        table.add_row(" ")

        # Batting summary
        table.add_row("[bold]Batting:[/bold]")

        batting_summary = []
        batting_summary.append("RBI: %d"%(summ['batting']['RBI']))
        for k in ['HR', '3B', '2B', '1B', 'BB', 'K', 'SAC', 'GDP']:
            bmap = summ['batting'][k]
            if len(bmap.items())==0:
                continue
            # This string is the line to print for this stat
            line = "%s: "%(k)
            # Re-sort the map by value, highest to lowest
            newbmap = {k: v for k, v in sorted(bmap.items(), reverse=True, key=lambda item: item[1])}
            # Assemble BatterName (count) list
            to_add = []
            for player, value in newbmap.items():
                if (k=='1B' or k=='K' or k=='BB') and value<2:
                    continue
                to_add.append("%s (%d)"%(player, value))
            if len(to_add)>0:
                # Make it pretty and print
                line += ", ".join(to_add)
                batting_summary.append(line)
        batting_summary.append("LOB: %d"%(summ['batting']['LOB']))
        table.add_row("\n".join(batting_summary))
        table.add_row(" ")

        # Baserunning summary
        if len(summ['baserunning']['CS'])>0 or len(summ['baserunning']['SB'])>0:
            table.add_row("[bold]Baserunning:[/bold]")

            baserunning_summary = []
            for k in ['SB', 'CS']:
                bmap = summ['baserunning'][k]
                if len(bmap.items())==0:
                    continue
                # This string is the line to print for this stat
                line = "%s: "%(k)
                # Re-sort the map by value, highest to lowest
                newbmap = {k: v for k, v in sorted(bmap.items(), reverse=True, key=lambda item: item[1])}
                # Assemble BatterName (count) list
                to_add = []
                for player, value in newbmap.items():
                    to_add.append("%s (%d)"%(player, value))
                if len(to_add)>0:
                    # Make it pretty and print
                    line += ", ".join(to_add)
                    baserunning_summary.append(line)

            table.add_row("\n".join(baserunning_summary))
            table.add_row(" ")

        return table

    def rich_weather_events(self):
        d = self.json_game_data

        table = Table(show_header=True, header_style="bold")

        we = "Weather Events:"
        table.add_column(we)
        for event in d['weather_events']:
            table.add_row(event)

        return table


class MarkdownView(TextView):
    def show(self):
        d = self.json_game_data

        # ---------------
        # game info
        print("")
        print("\n".join(self.md_info_header()))
        print("")

        # ---------------
        # box score
        if not self.line_only:
            print("")
            print("\n".join(self.md_box_score()))
            print("")

        # ---------------
        # line score
        if not self.box_only:
            print("")
            print("\n".join(self.md_line_score()))
            print("")

        # ---------------
        # pitching summary
        if not self.box_only and not self.line_only:
            print("")
            print("\n".join(self.md_pitching_summary()))
            print("")

        # ---------------
        # team summaries
        if not self.box_only and not self.line_only:
            for who in ['away', 'home']:
                print("")
                print("\n".join(self.md_team_summary(who)))
                print("")

        # ---------------
        # weather events
        if not self.box_only and not self.line_only:
            if len(d['weather_events'])>0:
                print("")
                print("\n".join(self.md_weather_events()))
                print("")

    def md_info_header(self):
        text_info_header = self.text_info_header()
        md_info_header = [j+"\n" for j in text_info_header]
        return md_info_header

    def md_box_score(self):
        """Make a box score for a text view"""
        d = self.json_game_data
        box_score = []

        def _make_box_score_row_md(name, row):
            rowstr = ""
            rowstr += "| %s | "%(name)
            for i in range(3):
                rowstr += "%3d | "%(row[i])
            return rowstr

        def _make_box_header_row_md():
            header = "|  | R | H | E |"
            return header

        def _make_box_header_sep_md():
            sep = "| --- | --- | --- | --- |"
            return sep

        box_score.append(_make_box_header_row_md())
        box_score.append(_make_box_header_sep_md())
        box_score.append(_make_box_score_row_md(d['info']['awayTeamNickname'], d['box_score']['away']))
        box_score.append(_make_box_score_row_md(d['info']['homeTeamNickname'], d['box_score']['home']))

        return box_score

    def md_line_score(self):
        """Make a line score for a markdown view"""
        d = self.json_game_data
        line_score = []

        def _make_line_score_row_md(name, line_row, box_row):
            rowstr = ""
            rowstr += "| %s | "%(name)
            for i in range(len(line_row)):
                rowstr += "%3d | "%(line_row[i])
            for i in range(len(box_row)):
                rowstr += "%3d | "%(box_row[i])
            return rowstr

        def _make_line_header_row_md(line_row):
            header = ""
            header += "|  | "
            for i in range(len(line_row)):
                header += "%3d | "%(i+1)
            header += " R | H | E |"
            return header

        def _make_line_header_sep_md(line_row):
            sep = "|"
            sep += " --- |"
            for i in range(len(line_row)):
                sep += " --- |"
            for i in range(3):
                sep += " --- |"
            return sep

        # Can use either home or away for these
        line_score.append(_make_line_header_row_md(d['line_score']['away']))
        line_score.append(_make_line_header_sep_md(d['line_score']['away']))
        # make the rows of the line score
        line_score.append(_make_line_score_row_md(d['info']['awayTeamNickname'], d['line_score']['away'], d['box_score']['away']))
        line_score.append(_make_line_score_row_md(d['info']['homeTeamNickname'], d['line_score']['home'], d['box_score']['home']))

        return line_score

    def md_pitching_summary(self):
        """Make a pitching summary for a markdown view"""
        d = self.json_game_data
        pitching_summary = []

        pitching_summary.append("| Pitching Summary |")
        pitching_summary.append("| --- |")
        pitching_summary.append("| **Winning Pitcher**: %s<br />KK: %d<br />BB: %d |"%(
            d['pitching_summary']['WP'],
            d['pitching_summary']['WP-K'],
            d['pitching_summary']['WP-BB'],
        ))
        pitching_summary.append("| **Losing Pitcher**: %s<br />KK: %d<br />BB: %d |"%(
            d['pitching_summary']['LP'],
            d['pitching_summary']['LP-K'],
            d['pitching_summary']['LP-BB'],
        ))

        return pitching_summary

    def md_team_summary(self, who):
        d = self.json_game_data
        summ = d['game_summary'][who]

        team_summary = []

        ts = "| Team Summary: %s |"%(d['info']['%sTeamNickname'%(who)])
        team_summary.append(ts)
        team_summary.append("| --- |")

        # Fielding summary
        if summ['fielding']['DP']>0 or summ['fielding']['TP']>0:
            team_summary.append("| **Fielding:** |")

            fielding_summary = []
            for k in ['DP', 'TP']:
                n = summ['fielding'][k]
                if n > 0:
                    fielding_summary.append("%s: %d"%(k, n))

            team_summary.append("| " + " <br />".join(fielding_summary) + " |")

        # Batting summary
        team_summary.append("| **Batting:** |")

        batting_summary = []
        batting_summary.append("RBI: %d"%(summ['batting']['RBI']))
        for k in ['HR', '3B', '2B', '1B', 'BB', 'K', 'SAC', 'GDP']:
            bmap = summ['batting'][k]
            if len(bmap.items())==0:
                continue
            # This string is the line to print for this stat
            line = "%s: "%(k)
            # Re-sort the map by value, highest to lowest
            newbmap = {k: v for k, v in sorted(bmap.items(), reverse=True, key=lambda item: item[1])}
            # Assemble BatterName (count) list
            to_add = []
            for player, value in newbmap.items():
                if (k=='1B' or k=='K' or k=='BB') and value<2:
                    continue
                to_add.append("%s (%d)"%(player, value))
            if len(to_add)>0:
                # Make it pretty and print
                line += ", ".join(to_add)
                batting_summary.append(line)
        batting_summary.append("LOB: %d"%(summ['batting']['LOB']))
        team_summary.append("| " + " <br />".join(batting_summary) + " |")
        return team_summary

    def md_weather_events(self):
        d = self.json_game_data
        weather_summary = []

        we = "| **Weather Events:** |"
        weather_summary.append(we)
        weather_summary.append("| --- |")
        for event in d['weather_events']:
            weather_summary.append("| " + event + " |")

        return weather_summary

