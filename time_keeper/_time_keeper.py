#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""Time keeper - Manage time spent on todo.txt projects.
"""

import datetime as dt
import subprocess as sp

# the time_keeper.txt format is as follows:
# 2014-05-26 Project1 1:37
# 2014-05-26 Project1 0:12

weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                 "Saturday", "Sunday"]
                 # TODO: can we get those localized from somewhere else?


class ProjectError(Exception):
    """Raised on operations on invalid projects.
    """

    pass


def get_projects():
    """Get TODO.txt projects.
    """

    # call 'todo.sh listproj' and parse output

    try:
        result = sp.Popen(["todo.sh", "listproj"], stdout=sp.PIPE,
                          stderr=sp.PIPE).communicate()[0]
    except OSError:
        print("todo.sh could not be called.")
        result = None
    else:
        result = [item.replace("+", "") for item in result.split("\n")]

    # possibly result now has an '' item, remove that:
    try:
        result.remove("")
    except ValueError:
        pass

    return result


def book_time(tk_file, time_spent, project, date):
    """Book time on project.
    """

    # check if project is valid:
    _check_project(project)

    # append time to log:
    hours, minutes = int(time_spent[0]), int(time_spent[1])
    line = "%s %s %s:%s\n"%(date, project, hours, minutes)
    _append_to_log(tk_file, line)


def archive(tk_filename, archive_filename):
    """End current tracking period.

    Move all data to archive and delete contents of log.
    """

    log_curr_period = _read_log(tk_filename)

    dates, projects, durations = sort_log(log_curr_period)

    archive_file = file(archive_filename, mode="a")
    archive_file.write("\nTimekeeping period ended %s:\n"
                       %dt.date.today().isoformat())

    for date, project, duration in zip(dates, projects, durations):
        archive_file.write("%s %s %s\n"%(date, project, duration))

    archive_file.close()

    # close current reporting period by deleting content of log:
    f = file(tk_filename, mode="w").close()  # open for writing and closing deletes contents

    print("Activities moved to archive, started new time keeping period.")


def get_report(tk_file, report_dates=None, report_projects=None):
    """Create report of time spent on projects in current tracking period.

    Parameters
    ----------
    tk_file : string
        Log file name.
    report_dates : iterable
        A list of dates in ISO format for which a report is to be generated.
    report_projects : iterable
        A list of projects for which a report is to be generated.

    Returns
    -------
    report : string

    Note
    ----
    If neither report_dates or report_projects is given, all dates in current
    reporting report are evaluated.
    """

    # TODO: this function has too many branches, too many decisions and does too much in general

    report = ""

    log_lines = _read_log(tk_file)
    if(len(log_lines) == 0):
        report = "No activities booked yet."
        return report

    dates, projects, durations = sort_log(log_lines)

    # for kinds of reporting, all bookings on individual projects will be
    # summed up and reported. create and initialize a dictionary that holds
    # summed effort:
    summed_times = {}
    unique_projects = _get_unique_items(projects)
    for unique_project in unique_projects:  # initialize summed times
        summed_times[unique_project] = 0

    # if specific date given:
    if(report_dates is not None):
        for report_date in report_dates:
            report += (report_date + " ("
                       + _get_weekday_name_from_isoformat(report_date)
                       + "):\n")
            # for each date, go through the whole list of dates:
            for date, project, duration in zip(dates, projects, durations):
                if(date == report_date):
                    report += "\t%s: %s\n"%(project, duration)
                    summed_times[project] += _duration_to_minutes(duration)

    elif(report_projects is not None):
        # report on a per project-base first:

        summed_times = {}
        # remove leading '+' for all report_projects:
        report_projects = [item[1:] for item in report_projects]
        for project in report_projects:
            _check_project(project)
            report += str(project) + ":\n"
            summed_times[project] = 0

            for date, log_project, duration in zip(dates, projects, durations):
                if(project == log_project):
                    report += "\t%s: %s\n"%(date, duration)
                    summed_times[project] += _duration_to_minutes(duration)

    else:  # report for whole reporting period wanted
        curr_date = None

        for date, project, duration in zip(dates, projects, durations):
            if(date != curr_date):
                report += (date + " (" + _get_weekday_name_from_isoformat(date)
                           + "):\n")
                curr_date = date
            report += "\t%s: %s\n"%(project, duration)
            summed_times[project] += _duration_to_minutes(duration)

    # finally report summed times:
    report += "\nSummed times spent:\n"
    for project in summed_times.keys():
        report += (project + ": "
                   + str(_minutes_to_duration(summed_times[project]))
                   + "\n"
                   )

    return report


def sort_log(log_lines):
    """Sort log.

    Parameters
    ----------
    log_lines : list
        Log lines as returned by a _read_log() call.

    Returns
    -------
    dates, projects, durations : tuples
        Dates, projects and durations booked on projects sorted by date.
    """

    dates, projects, durations = [], [], []

    # go through all log lines, split the lines and append each item to the
    # corresponding list
    for line in log_lines:
        date, project, duration = line.split()
        date = dt.date(*map(int, date.split("-")))
        dates.append(date.isoformat())  # convert back to string representation
        projects.append(project)
        durations.append(duration)

    # sort all list according to dates:
    dates, projects, durations = zip(*sorted(zip(dates, projects, durations)))

    return dates, projects, durations


def _read_log(tk_file):
    try:
        lines = file(tk_file, mode="r").readlines()
    except IOError:
        print("Error reading logfile. Have you booked time yet?")
        lines = ""

    return lines


def _get_date_tuple_from_string(date_string):
    """For the string '2013-05-14, return the tuple (2014, 5, 14).
    """

    return tuple(map(int, date_string.split("-")))


def _check_project(project):
    """Check if project is valid.

    Parameters
    ----------
    project : string
        A project name
    """

    projects = get_projects()
    if project in projects:
        pass
    else:
        raise ProjectError("Project %s not in todo.txt file."%project)


def _append_to_log(tk_file, line):
    """Write a line to time keeper's log.

    Parameters
    ----------
    tk_file : string
        The log's file name.
    line : string
        The line to add.
    """

    with file(tk_file, mode="a") as f:
        f.write(line)


def _get_weekday_name_from_isoformat(date):
    """Get weekday name from ISO format string date representation.

    Parameters
    ----------
    date : string
        A string such as 2014-07-22.

    Returns
    -------
    weekday : string
        A string, e.g. 'Thursday'.

    Note
    ----
    The names are not localized. Names are hardcoded.
    """

    dt_obj = dt.date(*_get_date_tuple_from_string(date))
    weekday = dt_obj.isoweekday()

    return weekday_names[weekday - 1]


def _duration_to_minutes(duration):
    """Convert a duration given as hours:minutes to minutes.

    Parameters
    ----------
    duration : str

    Returns
    -------
    min : int
    """

    hours, minutes = duration.split(":")

    return int(hours)*60 + int(minutes)


def _minutes_to_duration(minutes):
    """Convert a number of minutes to a duration string in the form
    hours:minutes.

    Parameters
    ----------
    minutes : int

    Returns
    -------
    duration : str
    """

    # TODO: this routine is slightly non-orthogonal to _get_time() in the main script

    hours, minutes = divmod(minutes, 60)

    return str(hours) + ":" + "%02d"%(minutes)


def _get_unique_items(iterable):
    """Get unique items in an container.

    Parameters
    ----------
    iterable : container

    Returns
    -------
    unique_items : container
        The container of unique items. Is of the same type as the input
        container.
    """

    in_type = type(iterable)

    unique_items = in_type(set(iterable))

    return unique_items
