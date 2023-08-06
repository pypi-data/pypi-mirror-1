#   Copyright (c) 2007 Mikeal Rogers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import commands
import os

def test_failing_test():
    test_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                'files', 'failures', 'test_fail.py'))
    outs = commands.getoutput('functest '+test_file)
    assert outs.find('Passed: 0, Failed: 1, Skipped: 0') is not -1



