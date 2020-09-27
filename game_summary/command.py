import sys
import os
import json
import configargparse
from .view import MarkdownView, TextView, RichView, JsonView


def main(sysargs = sys.argv[1:]):

    p = configargparse.ArgParser()

    p.add('-v',
          '--version',
          required=False,
          default=False,
          action='store_true',
          help='Print program name and version number and exit')

    p.add('-c',
          '--config',
          required=False,
          is_config_file=True,
          help='config file path')

    p.add('game_id',
          help='Specify the game ID of the game to summarize (repeat flag to specify multiple game IDs)')

    # View format
    g = p.add_mutually_exclusive_group()
    g.add('--markdown',
          action='store_true',
          default=False,
          help='Output game summaries in markdown format')
    g.add('--text',
          action='store_true',
          default=False,
          help='Output game summaries in plain text format')
    g.add('--rich',
          action='store_true',
          default=False,
          help='Output game summaries using rich command-line text')
    g.add('--json',
          action='store_true',
          default=False,
          help='Output game summaries in JSON format')

    # More view options
    h = p.add_mutually_exclusive_group()
    h.add('--box-only',
          action='store_true',
          required=False,
          default=False,
          help='Only show the box score from the game')
    h.add('--line-only',
          action='store_true',
          required=False,
          default=False,
          help='Only show the line score from the game')

    # Add an --events flag to print each scoring event like the discord bot

    # -----

    if len(sysargs)==0:
        # Print help, if no arguments provided
        p.print_help()
        exit(0)
    elif '-v' in sysargs or '--version' in sysargs:
        # If the user asked for the version,
        # print the version number and exit.
        # (Note: this is done separate from
        # argparse, because otherwise the user
        # has to ALSO provide a game ID to get
        # the --version flag to work. ugh.)
        from . import _program, __version__
        print(_program, __version__)
        sys.exit(0)

    # Parse arguments
    options = p.parse_args(sysargs)

    # If the user did not specify output format, use text
    if (not options.markdown) and (not options.text) and (not options.rich) and (not options.json):
        options.json = True
        if options.box_only or options.line_only:
            print("The --box-only and --line-only options require a non-JSON format to be specified:")
            print("Use one of the following: --markdown | --rich | --text")
            sys.exit(0)

    if options.markdown:
        v = MarkdownView(options)
        v.show()
    elif options.text:
        v = TextView(options)
        v.show()
    elif options.rich:
        v = RichView(options)
        v.show()
    elif options.json:
        v = JsonView(options)
        v.show()


if __name__ == '__main__':
    main()
