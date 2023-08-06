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

import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite
import sys, os, tempfile


def setUp(test):
    tmp = tempfile.mkdtemp()
    configFile = os.path.join(tmp, 'timerep')
    test.globs['configFile'] = configFile

def test_suite():
    return unittest.TestSuite((
         DocFileSuite('README.txt',
                setUp=setUp,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
             ),
         DocFileSuite('hook.txt',
                setUp=setUp,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
             ),
         ),
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

