#!/usr/bin/env python
#
# Copyright 2008 Bernd Roessl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
import pytz
from datetime import datetime, timedelta
import time
import urllib
import optparse
import atom

import gdata.calendar
import gdata.calendar.service

from calendar import CalendarConsumer
from hooks import hookHandler

TIMEZONE = pytz.timezone(time.tzname[0])

options = {}

class Clockin(CalendarConsumer):

    options = options

    def formatDate(self, dt):
        dt = dt.replace(microsecond = 0)
        dt = dt.replace(second = 0)
        grain = int(self.config['grain'])
        minute = (dt.minute - (dt.minute % grain) + (dt.minute % grain >= (grain/2+grain%2) and grain or 0))
        if minute == 60:
            dt = dt + timedelta(seconds=3600)
            minute = 0
        dt = dt.replace(minute = minute)
        return dt.isoformat()

    def parseDate(self, datestring):
        isoformat = "%Y-%m-%dT%H:%M:%S"
        return time.strptime(datestring[:19], isoformat)

    @property
    def now(self):
        return self.formatDate(datetime.now(TIMEZONE))

    @property
    def forcedTime(self):
        first = second = None
        if not options.forcedtime:
            return first, second

        parts = [p.strip() for p in options.forcedtime.split("-")]
        firstPart = parts[0].split(':')
        if (   len(firstPart) != 2
            or not firstPart[0].isdigit()
            or not firstPart[1].isdigit()):
            raise ValueError("First part is not a valid time")
        firstDate = datetime.now(TIMEZONE)
        firstDate = firstDate.replace(hour = int(firstPart[0]), minute=int(firstPart[1]))
        first = self.formatDate(firstDate)
        if len(parts) > 1:
            secondPart = parts[1].split(':')
            if (   len(secondPart) != 2
                or not secondPart[0].isdigit()
                or not secondPart[1].isdigit()):
                raise ValueError("Second part is not a valid time")
            secondDate = datetime.now(TIMEZONE)
            secondDate = secondDate.replace(hour = int(secondPart[0]), minute=int(secondPart[1]))
            second = self.formatDate(secondDate)
        return first, second

    @property
    def entries(self):
        calID = urllib.unquote(self.calendar.GetSelfLink().href.split("/")[-1])
        query = gdata.calendar.service.CalendarEventQuery(calID)
        yesterday = datetime.today() - timedelta(1)
        tomorrow = datetime.today() + timedelta(1)
        query.start_min = yesterday.isoformat()
        query.start_max = tomorrow.isoformat()
        query.orderby = 'starttime'
        feed = self.service.CalendarQuery(query)
        return feed.entry

    @property
    def lastEntry(self):
        feed = self.entries
        if len(feed) > 0:
            return feed[0]
        return None

    def hasPending(self):
        entry = self.lastEntry
        if entry is not None:
            if entry.when[0].end_time == entry.when[0].start_time:
                mess = '%s (%s) %s - now' % (entry.title.text,
                                             entry.content.text,
                                             entry.when[0].start_time[11:16])
            else:
                mess = 'no entry in progress'
        else:
            mess = 'no entry in progress'
        print mess

    def hasConflict(self, start, end):
        startdate = self.parseDate(start)
        enddate = self.parseDate(end)
        for e in self.entries:
            entrystart = self.parseDate(e.when[0].start_time)
            entryend = self.parseDate(e.when[0].end_time)
            if not (startdate >= entryend or enddate <= entrystart):
                return "in conflict with %s - %s %s (%s)" % (e.when[0].start_time[11:16],
                                                             e.when[0].end_time[11:16],
                                                             e.title.text,
                                                             e.content.text)
        return ""

    def listEntries(self):
        entries = self.entries
        entries.reverse()
        print ""
        if len(entries) == 0:
            print "no entries in calendar"
        for i in range(len(entries)):
            e = entries[i]
            prefix = e.when[0].start_time[8:10] == self.now[8:10] and 9*" " or "yesterday"
            start = e.when[0].start_time[11:16]
            end = e.when[0].end_time[11:16]
            if start == end:
                end = 5*" "
            if i > 0 and e.when[0].start_time != entries[i-1].when[0].end_time:
                print ""
            mess = '%s %s - %s   %s (%s)' % (prefix,
                                             start,
                                             end,
                                             e.title.text,
                                             e.content.text)
            print mess
        print ""

    def stopLastEntry(self):
        lastEntry = self.lastEntry
        if lastEntry is not None:
            if lastEntry.when[0].end_time == lastEntry.when[0].start_time:
                isYesterday = False
                if options.forcedtime:
                    stopTime = self.forcedTime[0]
                    stopTimeObject = datetime.fromtimestamp(time.mktime(self.parseDate(stopTime)))
                    if stopTimeObject > datetime.now():
                        # stop-time in future -> assume user means yesterday
                        stopTimeYesterday = stopTimeObject - timedelta(days=1)
                        stopTime = self.formatDate(stopTimeYesterday)
                        isYesterday = True
                else:
                    stopTime = self.now

                if self.parseDate(stopTime) > self.parseDate(lastEntry.when[0].end_time):
                    # stop that entry
                    lastEntry.when[0].end_time = stopTime

                    hookHandler.process("before_stop", lastEntry, self)
                    self.service.UpdateEvent(lastEntry.GetEditLink().href, lastEntry)
                    hookHandler.process("after_stop", lastEntry, self)

                    mess = '%s (%s) stopped. %s - %s %s' % (lastEntry.title.text,
                                                         lastEntry.content.text,
                                                         lastEntry.when[0].start_time[11:16],
                                                         lastEntry.when[0].end_time[11:16],
                                                         isYesterday and "yesterday" or "")
                elif self.parseDate(stopTime) == self.parseDate(lastEntry.when[0].end_time):
                    # last entry was to short -> remove it
                    hookHandler.process("before_delete", lastEntry, self)
                    self.service.DeleteEvent(lastEntry.GetEditLink().href)
                    hookHandler.process("after_delete", lastEntry, self)

                    mess = 'last entry to short, deleted.'
                else:
                    # stop-time older than start-time -> do nothing
                    mess = 'last entry not stopped.'
            else:
                mess = 'last entry has been stopped already.'
        else:
            mess = 'no entry to stop.'
        print mess

    def editLastEntry(self):
        entry = self.lastEntry
        if entry is not None:
            if options.title:
                entry.title = atom.Title(text=options.title)
            if options.description:
                entry.content = atom.Content(text=options.description)
            if options.forcedtime:
                entry.when[0].start_time = self.forcedTime[0]
                entry.when[0].end_time = self.forcedTime[1]

            hookHandler.process("before_edit", entry, self)
            self.service.UpdateEvent(entry.GetEditLink().href, entry)
            hookHandler.process("after_edit", entry, self)

            mess = '%s (%s) modified.' % (entry.title.text,
                                          entry.content.text)
        else:
            mess = 'no entry to edit.'
        print mess

    def continueLastEntry(self):
        lastEntry = self.lastEntry
        if lastEntry is not None:
            if lastEntry.when[0].end_time != lastEntry.when[0].start_time:
                entry = gdata.calendar.CalendarEventEntry()
                entry.title = atom.Title(text=lastEntry.title.text)
                entry.content = atom.Content(text=lastEntry.content.text)
                if options.forcedtime:
                    when = self.forcedTime[0]
                else:
                    when = self.now
                entry.when.append(gdata.calendar.When(start_time=when, end_time=when))
                insert_url = self.calendar.GetAlternateLink().href

                hookHandler.process("before_continue", entry, self)
                newEntry = self.service.InsertEvent(entry, insert_url)
                hookHandler.process("after_continue", entry, self)

                mess = 'continue %s (%s). %s -' % (entry.title.text,
                                                   entry.content.text,
                                                   entry.when[0].start_time[11:16])
            else:
                mess = 'last entry hasn\'t been stopped already.'
        else:
            mess = 'no entry to continue.'
        print mess

    def createNewEntry(self):
        entry = gdata.calendar.CalendarEventEntry()
        if options.title:
            entry.title = atom.Title(text=options.title)
            entry.content = atom.Content(text='')
        if options.description:
            entry.content = atom.Content(text=options.description)
        if options.forcedtime:
            when_start = when_end = self.forcedTime[0]
            if self.forcedTime[1] is not None:
                when_end = self.forcedTime[1]
        else:
            when_start = when_end = self.now
        hasConflict = self.hasConflict(when_start, when_end)
        if not hasConflict:
            entry.when.append(gdata.calendar.When(start_time = when_start,
                                                  end_time   = when_end))
            insert_url = self.calendar.GetAlternateLink().href

            hookHandler.process("before_new", entry, self)
            newEntry = self.service.InsertEvent(entry, insert_url)
            hookHandler.process("after_new", entry, self)

            if when_start == when_end:
                mess = '%s (%s) created. %s' % (newEntry.title.text,
                                                newEntry.content.text,
                                                newEntry.when[0].start_time[11:16])
            else:
                mess = '%s (%s) created. %s - %s' % (newEntry.title.text,
                                                     newEntry.content.text,
                                                     newEntry.when[0].start_time[11:16],
                                                     newEntry.when[0].end_time[11:16])

        else:
            mess = hasConflict
        print mess


def main():
    parser = optparse.OptionParser(
        description='command line time-reporting for google calendar',
        usage='%prog [options]')
    parser.add_option("-n", "--new",
                      action="store_true", dest="new", default=False,
                      help="create a new entry and stop the last one.")
    parser.add_option("-l", "--last",
                      action="store_true", dest="last", default=False,
                      help="edit the last 'open' time entry.")
    parser.add_option("-s", "--stop",
                      action="store_true", dest="stop", default=False,
                      help="stop the last entry if possible.")
    parser.add_option("-c", "--continue",
                      action="store_true", dest="cont", default=False,
                      help="continue the last entry if possible.")
    parser.add_option("-t", "--title", action="store",
                      dest="title", default='', type="string",
                      help="the title of the entry")
    parser.add_option("-d", "--description", action="store",
                      dest="description", default='', type="string",
                      help="the description of the entry")
    parser.add_option("-f", "--forcetime", action="store",
                      dest="forcedtime", default='', type="string",
                      help="force time (iE: 13:45) or timerange (iE: 11:05 - 13:45)")
    global options
    (options, args) = parser.parse_args()

    clock = Clockin()
    if options.new:
        # adding new item
        if parser.largs:
            parser.values.title = parser.largs.pop(0)
        if parser.largs:
            parser.values.description = parser.largs.pop(0)
        if parser.largs:
            parser.values.forcedtime = parser.largs.pop(0)

        if options.title:
            clock.stopLastEntry()
            clock.createNewEntry()
        else:
            parser.print_help()
            sys.exit(1)

    elif options.last:
        # modify the last (current) item
        if parser.largs:
            parser.values.title = parser.largs.pop(0)
        if parser.largs:
            parser.values.description = parser.largs.pop(0)
        if parser.largs:
            parser.values.forcedtime = parser.largs.pop(0)

        if options.title or options.description or "-" in options.forcedtime:
            clock.editLastEntry()
        else:
            clock.hasPending()

    elif options.cont:
        # continue a previously stopped item
        if parser.largs:
            parser.values.forcedtime = parser.largs[0]
        clock.continueLastEntry()

    elif options.stop:
        # stop the last (current) item
        if parser.largs:
            parser.values.forcedtime = parser.largs[0]
        clock.stopLastEntry()

    else:
        # list itmes
        clock.listEntries()
