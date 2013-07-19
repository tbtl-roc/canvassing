Canvassing Utilities
====================

This repository contains code useful for organizing weekly neighborhood
canvassing.  We want to build a network of people facing foreclosure and
eviction who want to stay in their homes and fight back.

We have a dump of foreclosures available at
http://monroe-threebean.rhcloud.com/export.csv and we want to organize those
according to some criteria to make going door-to-door easier.

``make_addresses.py`` is the main script.  Take a look at that file and its
docstrings for more information.

Notes on usage
--------------

Open up a terminal by going to ``Applications -> Activities -> Terminal``.

At the "command prompt" type ``cd devel/canvassing``.

Run the program by typing ``python make_addresses.py``.

It may complain that it does not have access to the latest foreclosures.  If
this is the case, it will ask you to run another program that looks something
like ``wget .....``.  Run that -- it will take a moment, but it will download
the latest list of city foreclosures.  Once it is done, run
``python make_addresses.py``.

It is also going to need a file that it expects to be named
"alltime-knowledge.csv".  You can generate this file from the 14621
foreclosures google docs spreadsheet by visiting google docs, opening up
that spreadsheet, clicking on ``File`` and *exporting* it as a
"comma-separated value" file.  By default it will download it to a location
on the computer called ``~/Downloads/``.  Once you have exported/downloaded
it, you need to move it into a place where the make_addresses.py program can
find it by running this command on the command prompt:

``mv ~/Downloads/14621\ foreclosures\ -\ 14621.csv alltime-knowledge.csv``

Whew!

----

You need to produce two kinds of documents for canvassing.  The first is the
maps.  The "make_addresses.py" program should have printed out 4 super-long
google maps URLs.  Copy and paste each one, opening them up in the browser.
You can print them from google maps there.

The second kind of document is the spreadsheet which lists the addresses for
each team one by one.  Those are "comma separated value files" and they can be
found in the ``output/`` folder.  Check them out by going to ``Places -> Home
Folder``.  Click on ``devel`` and then again on ``canvassing`` and then again
one ``output``.  Do you see them?

To print them nicely for canvassers to use, open up google docs at
https://docs.google.com.  Upload each of the teams' sheets and print them from
there.

Advanced usage
--------------

The ``make_addresses.py`` script has lots of "options" which you can see listed
if you type ``python make_addresses.py --help`` at the "command prompt".  By
default, it creates sheets and maps for 4 teams of people.  You can change
that to as few or as many as you want by running
``python make_addresses.py --number-of-teams 2`` (for instance, to make sheets
for only two teams).

By default it uses the 14621 area code.  You can change that by specifying
a ``--zipcode`` option like:  ``python make_addresses.py --zipcodes 14610``
(for instance, to check out the 14610 zip code).
