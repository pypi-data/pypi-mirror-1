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
import ConfigParser

BLANK_TEMPLATE = """
[clockin]
username = user@example.com
password = secret
calendar = time
grain = 5
addons = 
"""

class ClockinConfig(ConfigParser.ConfigParser):

    _section = 'clockin'

    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults)
        self.load()

    @property
    def configFile(self):
        homedir = os.path.expanduser("~")
        return os.path.join(homedir, '.clockin')

    def createConfig(self):
        cf = open(self.configFile, "w")
        cf.write(BLANK_TEMPLATE)
        cf.flush()

    def load(self):
        if not os.path.exists(self.configFile):
            self.createConfig()
        self.read(self.configFile)

    def __getitem__(self, key):
        return self.get(self._section, key)

    def __setitem__(self, key, value):
        self.set(self._section, key, value)
