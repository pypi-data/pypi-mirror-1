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
import config


class HookHandler(object):

    config = None
    addons = set()

    def __init__(self):
        self.config = config.ClockinConfig()
        self.loadAddOns()

    def loadAddOns(self):
        addonFolder = ''
        try:
            addonFolder = self.config['addons']
        except: pass
        if os.path.exists(addonFolder):
            sys.path.append(addonFolder)
            self.addons = set([f.split(".")[0] for f in os.listdir(addonFolder)])

    def process(self, method, entry, reporter):
        for addon in self.addons:
            try:
                exec "import %s" % addon
                eval("%s.%s(entry, reporter)" % (addon, method))
            except:
                pass

hookHandler = HookHandler()
