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

import gdata
import gdata.calendar
import gdata.calendar.service

feed = gdata.GDataFeed()

class StubService(gdata.calendar.service.CalendarService):

    def InsertEvent(self, event, insert_url):
        feed.entry.insert(0, event)
        event.link = [gdata.EntryLink(rel='edit', href=event.__repr__())]
        return event

    def DeleteEvent(self, edit_url):
        for e in feed.entry:
            if e.__repr__() == edit_url:
                feed.entry.remove(e)
                break

    def UpdateEvent(self, edit_url, event):
        for e in feed.entry:
            if e.__repr__() == edit_url:
                e = event
                break

    def CalendarQuery(self, query):
        return feed


class StubCalendar(gdata.calendar.CalendarListEntry):

    def GetAlternateLink(self):
        return gdata.EntryLink(rel='alt', href='nohost')

    def GetSelfLink(self):
        return gdata.EntryLink(rel='self', href='nohost')
