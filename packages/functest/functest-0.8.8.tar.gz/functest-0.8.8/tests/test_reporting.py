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

def test_reporting():
    test_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                'files', 'reports', 'test_reports.py'))
    outs = commands.getoutput('functest '+test_file)
    assert 'all tests list [<function setup_module at' in outs
    assert '--stdout--capture in stdout' in outs
    assert 'Finished test_function: test_stub' in outs
    assert 'Finished setup_module:' in outs
    assert 'Finished teardown_module:' in outs
    

