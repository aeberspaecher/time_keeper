Time Keeper
===========

Rationale
---------

You keep track of your tasks and projects with a TODO.txt tool? And you want to
or have to keep track how much time you spent on which project? You don't want
to punch in and out when you start something new, but rather fancy a more
coarse grained overview? Is it enough for you to add hours to a project once or
twice a day? Then this is for you.

Files used
----------

First, there's your todo.txt. Then, there's the two files

::

    tk.txt: time keeping for the current period

    tk_archive.txt: your time keeping archive since the beginning of the
    beginning

Installation
------------

Configure and install::

    ./waf configure
    sudo ./waf install

The location of your todo.txt file, and time_keeper's tk.txt, tk_report.txt
files are read from the environment variable ``$TIMEKEEPERPATH``.

Usage
-----

Time Keeper is used through the ``tk`` command line utility.

Getting help::

    tk --help  # list options

Booking time on projects::

    tk book 1h +ComplicatedProject  # book one hour on ComplicatedProject
    tk book 27min +AProject --when=-3d  # book 27min of work spent on AProjct three days ago
    tk book 1h 01min +AProject --when=2014-06-29


Reporting activity::

    tk report  # print time keeping report since last archive
    tk report 2014-05-22  # print time booked for May 22th 2014
    tk report +Project1 +AnotherProject  # report time spent on projects Project1 and AnotherProject

Starting a new tracking period::

    tk archive  # archive current time keeping
