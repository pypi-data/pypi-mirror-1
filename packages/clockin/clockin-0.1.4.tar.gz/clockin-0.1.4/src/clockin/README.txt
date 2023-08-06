Tests for clockin
-----------------

The configuration of clockin::
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> from clockin.config import ClockinConfig
    >>> ClockinConfig.configFile = configFile
    >>> config = ClockinConfig()
    >>> config
    <clockin.config.ClockinConfig instance at ...>

Accessing any config option the first time without to edit them manually
will create a file with the required options::

    >>> print config['username']
    user@example.com

    >>> print config['password']
    secret

    >>> print config['calendar']
    time


The time report utility::
~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> import gdata
    >>> import gdata.calendar
    >>> import gdata.calendar.service
    >>> from clockin import testing

    >>> def createService(inst):
    ...     inst.service = testing.StubService()

    >>> def getCalendar(inst):
    ...     inst.calendar = testing.StubCalendar()

    >>> from clockin.clockin import Clockin
    >>> Clockin.createService = createService
    >>> Clockin.getCalendar = getCalendar

    >>> rep = Clockin()
    >>> rep
    <clockin.clockin.Clockin object at ...>

There is a method to format a date to a required format to deal with gdata. The
method consists of three steps:

 1.) set all unnessesary properties liks seconds and microseconds to zero
 2.) calculate the actual minute in a 5 minute raster
 3.) format the date

So first we need a date::

    >>> from datetime import datetime
    >>> from clockin.clockin import TIMEZONE
    >>> d = datetime(2008, 8, 15, 23, 34, 0, 0, TIMEZONE)
    >>> d
    datetime.datetime(2008, 8, 15, 23, 34, tzinfo=...)

As we can see the minutes of the date get set to value within a raster of
5 minutes. That means if the minute of a given date is set to 1 or 2 the
resulting value will be 0. if the minute was set to 3 or 4 the resulting
value will be 5::

    >>> print rep.formatDate(d)
    2008-08-15T23:35:00+01:00

Now let's set the minute to 2 so the resulting minutes will be set to 0::

    >>> d = d.replace(minute = 32)
    >>> print rep.formatDate(d)
    2008-08-15T23:30:00+01:00

We have to take care on the last 5 minutes of an hour. In case the minute
is 58 which get rounded to 0 we also have to add one hour (which can cause
a new day or month or year)::

    >>> d = d.replace(minute = 58)
    >>> print rep.formatDate(d)
    2008-08-16T00:00:00+01:00

The grain will be configurable in the config file. So we can set the grain
to a different value than the default value. Let's set it to 15 minutes::

    >>> rep.config['grain'] = "15"

    >>> d = d.replace(minute = 37)
    >>> print rep.formatDate(d)
    2008-08-15T23:30:00+01:00

    >>> d = d.replace(minute = 53)
    >>> print rep.formatDate(d)
    2008-08-16T00:00:00+01:00

We will set back the grain to the dafault value to keep existing tests running::

    >>> rep.config['grain'] = "5"

There is also one method called 'now' which returns the formated and rounded
date::

    >>> rep.now.startswith(rep.formatDate(datetime.now()))
    True

But now lets test the utility in action. calling the utlity without any options
the util will list all items of today and yesterday. But currently our
calendar is empty::

    >>> from clockin.clockin import main
    >>> import sys
    >>> sys.argv = ['clockin']
    >>> main()
    <BLANKLINE>
    no entries in calendar
    <BLANKLINE>

It is a common task to check out the last item because this is the current
item which is in progress::

    >>> sys.argv = ['clockin', '-l']
    >>> main()
    no entry in progress

Now let's create a brand new entry in our time reporting calendar::

    >>> sys.argv = ['clockin', '-n']
    >>> main()
    Traceback (most recent call last):
    ...
    SystemExit: 1

Of course we have to enter a title for the entry::

    >>> sys.argv = ['clockin', '-n', '-t', 'title of entry']
    >>> main()
    no entry to stop.
    title of entry () created. ...

It is also possible to pass a description for the entry::

    >>> sys.argv = ['clockin', '-n', '-t', 'title', '-d', 'description']
    >>> main()
    last entry to short, deleted.
    title (description) created. ...

There is a shortcut for creating new entries::

    >>> sys.argv = ['clockin', '-n', 'title 2', 'description 2']
    >>> main()
    last entry to short, deleted.
    title 2 (description 2) created. ...

It is also possible to force the time range which will be used for handling
calendar entries::

    >>> sys.argv = ['clockin', '-n', '-t', 'forced', '-f', '12:32 - 13:18']
    >>> main()
    last entry not stopped.
    forced () created. 12:30 - 13:20

And of course in shortcut format::

    >>> sys.argv = ['clockin', '-n', 'forced', 'description', '15:18-16:51']
    >>> main()
    last entry has been stopped already.
    forced (description) created. 15:20 - 16:50

There is some conflict resolution to avoid overlaping  entries::

    >>> sys.argv = ['clockin', '-n', 'conflict', '-f', '15:00-15:30']
    >>> main()
    last entry has been stopped already.
    in conflict with 15:20 - 16:50 forced (description)

    >>> sys.argv = ['clockin', '-n', 'conflict', '-f', '16:45-17:00']
    >>> main()
    last entry has been stopped already.
    in conflict with 15:20 - 16:50 forced (description)

    >>> sys.argv = ['clockin', '-n', 'conflict', '-f', '15:40-16:10']
    >>> main()
    last entry has been stopped already.
    in conflict with 15:20 - 16:50 forced (description)

    >>> sys.argv = ['clockin', '-n', 'conflict', '-f', '15:10-16:55']
    >>> main()
    last entry has been stopped already.
    in conflict with 15:20 - 16:50 forced (description)

Appropos forced time. The method will do some validation and parse the
given strings to proper time objects::

    >>> sys.argv = ['clockin']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    (None, None)

Now lets set pass in a date::

    >>> sys.argv = ['clockin', '-f', '12:32']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    ('...T12:30:00...', None)

Or a time range::

    >>> sys.argv = ['clockin', '-f', '12:32 - 13:18']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    ('...T12:30:00...', '...T13:20:00...')

The passed values have to be valid times::

    >>> sys.argv = ['clockin', '-f', 'bla']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    Traceback (most recent call last):
    ...
    ValueError: First part is not a valid time

    >>> sys.argv = ['clockin', '-f', '19-20']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    Traceback (most recent call last):
    ...
    ValueError: First part is not a valid time

    >>> sys.argv = ['clockin', '-f', '10:']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    Traceback (most recent call last):
    ...
    ValueError: First part is not a valid time

    >>> sys.argv = ['clockin', '-f', '26:13']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    Traceback (most recent call last):
    ...
    ValueError: hour must be in 0..23

    >>> sys.argv = ['clockin', '-f', '19:72']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    Traceback (most recent call last):
    ...
    ValueError: minute must be in 0..59

    >>> sys.argv = ['clockin', '-f', '12:32 - now']
    >>> main()
    <BLANKLINE>
    ...
    >>> rep.forcedTime
    Traceback (most recent call last):
    ...
    ValueError: Second part is not a valid time

So now we can see some entries in the list::

    >>> sys.argv = ['clockin']
    >>> main()
    <BLANKLINE>
              15:20 - 16:50   forced (description)
    <BLANKLINE>
              12:30 - 13:20   forced ()
    <BLANKLINE>
              ... -         title 2 (description 2)
    <BLANKLINE>

We also can see if the time has been forced a leading entry has not been
stopped. So be carefully while doing this !!

Lets start with a clean calendar::

    >>> testing.feed.entry = []

    >>> sys.argv = ['clockin']
    >>> main()
    <BLANKLINE>
    no entries in calendar
    <BLANKLINE>

To test the stop and continue behaviour lets create a new entry::

    >>> sys.argv = ['clockin', '-n', '-t', 'stop-continue']
    >>> main()
    no entry to stop.
    stop-continue () created. ...

To stop a in progress entry just call the util with the option -s. But as we
have seen above to short entries get deleted. To short means shorter than 5
minutes::

    >>> sys.argv = ['clockin', '-s']
    >>> main()
    last entry to short, deleted.

So let's create one which start time is older than 5 minutes::

    >>> now = datetime.now()
    >>> from datetime import timedelta
    >>> now = now - timedelta(seconds=1800)
    >>> forcedTime = "%i:%i" % (now.hour, now.minute)

    >>> sys.argv = ['clockin', '-n', '-t', 'stop-continue-2', '-f', forcedTime]
    >>> main()
    no entry to stop.
    stop-continue-2 () created. ...

If there is no entry in the list the util will show this::

    >>> sys.argv = ['clockin', '-s']
    >>> main()
    stop-continue-2 () stopped. ... - ...

To continue a stopped entry just use the option -c::

    >>> sys.argv = ['clockin', '-c']
    >>> main()
    continue stop-continue-2 (). ... -

It isn't possible to continue the same entry twice::

    >>> sys.argv = ['clockin', '-c']
    >>> main()
    last entry hasn't been stopped already.
