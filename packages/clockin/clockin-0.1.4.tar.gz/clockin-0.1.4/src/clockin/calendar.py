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

import sys
import gdata.calendar
import gdata.calendar.service

import config


class CalendarConsumer(object):

    def __init__(self):
        self.config = config.ClockinConfig()
        self.createService()
        self.getCalendar()

    def createService(self):
        self.service = gdata.calendar.service.CalendarService()
        self.service.email = self.config['username']
        self.service.password = self.config['password']
        try:
            self.service.ProgrammaticLogin()
        except gdata.service.BadAuthentication:
            mess = "\n wrong username or password. edit %s\n"
            print mess % self.config.configFile
            sys.exit(1)

    def getCalendar(self):
        query = gdata.calendar.service.CalendarListQuery()
        cals = self.service.CalendarQuery(query)
        cals = [cal for cal in cals.entry if cal.title.text == self.config['calendar']]
        if len(cals) == 1:
            self.calendar = cals[0]
        else:
            mess = "\n calendar '%s' not found. create it or edit %s\n"
            print mess % (self.config['calendar'], self.config.configFile)
            sys.exit(1)
