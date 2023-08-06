Introduction
============

``haufe.ztop`` implements real-time Zope request analysis 
on top of haufe.requestmonitoring.


Requirements
============

* Zope 2.12.0b2 or higher (or a Zope 2 trunk checkout)
* haufe.requestmonitoring

Features
========

Before you can use any of these scripts you have to make sure that your Zope 
environment is known to the shell. A simple ``zopectl shell`` should be enough in most cases.

zanalyse
--------

Using ``zanalyse``::

    zanalyse [-i intervall] [-n numberLongRequests] [[-b] requestsBasename] [[-d] startDate]

prints an 'sar' like requests summary from the Zope requests log file
identified by *requestsBasename* and *startDate*.

The '-i' option specifies the granularity in minutes. It defaults to "10".

*requestsBasename* is either an instance tag (in which case it expands
to '/var/log/zope/*requestsBasename*/zope_requests.') or
the name of a zope requests file (not ending in '.') or of
a zope requests file family (ending in '.').
*requestsBasename* defaults to the instance tag 'Main'.
*startDate* must have the format year, month and day, each with 2 digits
e.g. '040803'. It defaults to the current date. Note that *requestsBasename*
must be an instance tag or a family name, when you default *startDate*.

Example output::

$ bin/zanalyse -i 10 instance

   short    load    reqs    rate     avg     min     max  median
            0.05     217    0.36     145       3   24640       5
           24640 /manage_menu
            1385 /manage_main
            1291 /Partner/manage_main
             552 /Applikationen/manage_main
             326 /Partner/manage_workspace
             301 /manage_main
             204 /p_/zopelogo_jpg
              94 /Administration/manage_main


ztop
----

Using ``ztop``::

    ztop [-i interval] [-s shortPeriod] [-m medPeriod] [-l longPeriod] 
         [-n numberLongRequests [-t time] [-r]] [[-b] requestsBasename] [[-d] startDate]

displays request information by analysis of the Zope requests log file
identified by *requestsBasename* and *startDate*.

Information contains summaries for up to three periods: 'short', 'med'
and 'long'. Their length is given by *shortPeriod* (default: 120),
*medPeriod* (default: 600) and *longPeriod* (default: 3600) in seconds.
Summaries contain load averaged over the period, number of finished
requests, request rate, average, min, max and median request times (in ms)
and the *numberLongRequests* (default: 3) longest requests in this period.
A period length of "0" suppresses information about this period.

The information is repeated every *interval* seconds.
*interval* defaults to the value of *shortPeriod* or 120.
A "0" value causes 'ztop' to stop after one display.

The '-t' option tells 'ztop' to display information for *time*
and then to stop. *time* is an ISO datetime or time value,
e.g. '2004-08-03T12:00:00' or '12:00:00'.

The '-r' option tells 'ztop' to display information for the last
restart time and then to stop. '-r' is equivalent to '-t <restartTime>'.
This is meant to facilitate the analysis of restarts.

*requestsBasename* is either an instance tag (in which case it expands
to '/var/log/zope/*requestsBasename*/zope_requests.') or
the name of a zope requests file (not ending in '.') or of
a zope requests file family (ending in '.').
*requestsBasename* defaults to the instance tag 'Main'.
*startDate* must have the format year, month and day, each with 2 digits
e.g. '040803'. It defaults to the current date. Note that *requestsBasename*
must be an instance tag or a family name, when you default *startDate*.

Example output::

$ bin/ztop -i 10 instance

   short    load    reqs    rate     avg     min     max  median
            0.00       4    0.03       9       4      25       4
              25 /Control_Panel/ZTop/manage_monitor
               4 /p_/ltab
               4 /p_/sp

     med    load    reqs    rate     avg     min     max  median
            0.00      20    0.03      17       4     146       8
             146 /Control_Panel/ZTop/manage_monitor
              25 /Control_Panel/ZTop/manage_monitor
              25 /Control_Panel/ZTop/manage_monitor

    long    load    reqs    rate     avg     min     max  median
            0.01     468    0.13      90       3   24640       6
           24640 /manage_menu
            1788 /Auftritte/manage_main
            1385 /manage_main

Installation
============

* add ``haufe.ztop`` to the ``eggs`` option of your buildout configuration
* create the related scripts using a dedicated ``ztop`` part::

      [buildout]
      parts = ... ztop ...


      [ztop]
      recipe = zc.recipe.egg
      eggs = haufe.ztop 


Author
======

Dieter Maurer, Haufe Mediengruppe

Maintainer
==========

Andreas Jung, Haufe Mediengruppe

License
=======

``haufe.ztop`` is published under the Zope Public License V 2.1 (ZPL)
See LICENSE.txt.


