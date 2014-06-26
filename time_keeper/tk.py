#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
from optparse import OptionParser
import datetime as dt

import time_keeper as tk


valid_commands = ("book", "report", "archive")
command_accepts_options = {"book": True, "report": True, "archive": False}
command_with_optional_options = {"book": False, "report": True, "archive": False}


def find_command(args):
    """Find command in argument list.
    """

    # TODO: refactor that loop below

    i = 0
    while(args[i].lower() not in valid_commands):
        i +=1
        if(i == len(args)):
            raise ValueError("No valid command given.")

    return args[i].lower()


def find_command_options(args, command):
    """Find options for given command.

    Returns everything in args that follows the command.
    """

    if(not command_accepts_options[command]):
        return ""

    # return everything in args that follows the command:
    args_lowercase = [arg.lower() for arg in args]
    command_index = args_lowercase.index(command)
    option_indices = slice(command_index+1, len(args))
    options = args[option_indices]

    if(len(options) == 0 and not command_with_optional_options[command]):
        raise ValueError("No options given for command '%s'"%command)
    else:
        return options


def find_project(args):
    for arg in args:
        if arg.startswith("+"): return arg[1:]


def _parse_time(list_repr):
    # create tuple (hours, minute) from strings such as "4h 30min", "12min"...
    hours, minutes = 0, 0
    a = {"h": 0, "min": 0, "hrs": 0, "mins": 0}
    for block in list_repr:
        for unit in ("h", "min", "hrs", "mins"):
            if(block.endswith(unit)):
                a[unit] += float(block.strip(unit))
        if(":" in block):
            h, m = tuple(map(float, block.split(":")))
            a["h"] += h
            a["min"] += m

    hours, minutes = _get_time(a["h"] + a["hrs"], a["min"] + a["mins"])

    # note that this allows "stupid" time durations such as "30min 4hrs 12mins"
    # this won't hurt, but gives the user the freedom to choose between
    # hrs/h and mins/min

    # TODO: add 'm', 'hours', 'minutes'?

    return hours, minutes


def _get_time(hours, minutes):
    # return time in valid format. e.g., 1h and 70 min should convert to
    # 2h 10 min

    hours, minutes = divmod(60*hours + minutes, 60)

    return hours, minutes


def _get_booking_date(opts):
    # dash indicates a date, eithe in 2011-01-11 format or in delta form
    # (-2d for two days ago):
    if(opts.when is not None):
        dash_count = opts.when.count("-")
        if(dash_count == 1 or opts.when.count("+") == 1):  # delta in days
            today = dt.date.today()
            delta = int(opts.when.strip("d"))
            # assume delta is given in days:
            booking_date = dt.date.today() + dt.timedelta(days=delta)
        elif(dash_count == 2):  # date
            year, month, day = arg.split("-")
            booking_date = dt.date(year, month, day)
        else:
            raise ValueError("Unknown booking date format.")
    else:
        booking_date = dt.date.today()  # assume the work was done today

    return booking_date


def _get_date_from_delta(opts):
    if opts.when.endswith("d"):
        pass
    else:
        raise ValueError("Invalid booking time given")


if(__name__ == '__main__'):
    # set paths to important files (todo.txt, tk.txt, tk_archive.txt):
    try:
        path = os.environ["TIMEKEEPERPATH"]
    except KeyError:
        print("Environment variable TIMEKEEPERPATH unset. Quitting.")
        sys.exit(1)

    tk_file = path + os.path.sep + "tk.txt"
    tk_archive_path = path + os.path.sep + "tk_archive.txt"

    # setup OptionParser and parse command line:
    prog_usage = """%prog book ProjectName 4h30min
    %prog report (2014-05-22/ProjectName)
    %prog archive
    """
    parser = OptionParser(usage=prog_usage)
    parser.add_option("-w", "--when", action="store", default=None,
                      dest="when", help="Book time to a different day (give either difference to today's date in days, e.g. -2d for the day before yesterday; or give the day, e.g. 1984-01-31)")
    (cmd_options, args) = parser.parse_args()

    # parse arguments:
    if(len(args) == 0):
        print("No command given, quitting.")
        sys.exit(0)

    command = find_command(args)
    opts = find_command_options(args, command)  # do we need find_command_options?

    if(command == "book"):
        project = find_project(args)
        booking_date = _get_booking_date(cmd_options)
        time_spent = _parse_time(args)
        tk.book_time(tk_file, time_spent, project, booking_date)
    elif(command == "report"):
        # interpret user input: does user want a report for a project, or for
        # one or several dates?
        report_projects = None
        report_dates = None
        long_opts = "".join(opts)
        if("+" in long_opts):  # user asks for a report on a project
            print("Project-based report is asked")
            report_projects = opts
        elif("-" in long_opts):
            print("Date-based report is asked")
            report_dates = opts

        report = tk.get_report(tk_file, report_dates=report_dates,
                               report_projects=report_projects)

        print report
    elif(command == "archive"):
        raise NotImplementedError("Archiving not implemented yet")
