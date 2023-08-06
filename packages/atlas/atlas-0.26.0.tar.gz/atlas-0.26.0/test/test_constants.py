#---------------------------------------------------------------------------
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#---------------------------------------------------------------------------
#
# Test Contants
#

ATLAS_BIN = '../../src/atlas.py'
TEST_DIR = 'out'

DEFAULT_MAIN_CPP_CONTENTS = 'int main() { return 0; }'
DEFAULT_ATLAS_CONTENTS = "CppExe(name = 'main', source = ['main.cpp'])"

MAIN_WITH_UTIL_CPP_CONTENTS = """
    #include "out/util.h"
    int main() {
    util_func();
    }
"""

UTIL_H_CONTENTS = """
    #ifndef UTIL_H__
    #define UTIL_H__
    void util_func();
    #endif  // UTIL_H__
"""

UTIL_CPP_CONTENTS = """
    #include "out/util.h"
    void util_func() {}
"""

DEFAULT_PY_TEST_CONTENTS = """
  #!/usr/bin/python
  import unittest
  class Test(unittest.TestCase):
    def test(self):
      self.assertTrue(True)
  unittest.main()
"""
