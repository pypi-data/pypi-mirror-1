#!/usr/bin/python
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
# cpp_test.py - C++ module tests
#
import os
import stat

import atlas_test
import test_constants
import util


DEFAULT_ATLAS_CONTENTS = """
    CppExe(name = 'main',
           source = ['main.cpp'])
"""

DEFAULT_ATLAS_LIB_CONTENTS = """
    CppLibrary(name = 'util',
               source = ['util.cpp'])
"""

INVALID_CPP_SOURCE = 'This is not C++ code'  # Won't compile


class ModuleTest(atlas_test.TestCase):

  def test_mod_cpp_exe(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
                source = ['main.cpp'])
        """)

    self.CreateFile('main.cpp',"int main() { return 0; }")

    target_list = ['main', 'main.o']
    self.Run('build', 'out:main')
    self.CheckBuildFilesExist(target_list)

    self.Run('clean', 'out:main')
    self.CheckBuildFilesExist(target_list, exists=False)

  def test_mod_cpp_exe_link_lib_absolute(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
               source = ['main.cpp'],
               library = ['//out:util'])
        CppLibrary(name = '//out:util',
                   source = ['util.cpp'])
        """)

    self.CreateFile('util.h', test_constants.UTIL_H_CONTENTS)
    self.CreateFile('util.cpp', test_constants.UTIL_CPP_CONTENTS)
    self.CreateFile('main.cpp',test_constants.MAIN_WITH_UTIL_CPP_CONTENTS)

    self.Run('build', 'out:main')

  def test_mod_cpp_exe_link_lib(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
               source = ['main.cpp'],
               library = ['util'])
        CppLibrary(name = 'util',
                   source = ['util.cpp'])
        """)

    self.CreateFile('util.h', test_constants.UTIL_H_CONTENTS)
    self.CreateFile('util.cpp', test_constants.UTIL_CPP_CONTENTS)
    self.CreateFile('main.cpp', test_constants.MAIN_WITH_UTIL_CPP_CONTENTS)

    self.Run('build', 'out:main')

  def test_mod_cpp_exe_link_fail(self):
    self.CreateFile('ATLAS', DEFAULT_ATLAS_CONTENTS)

    self.CreateFile('main.cpp',"""
        int missing();
        int main() {
          missing(); return 0;
        }
        """)

    output = self.Run('build', 'out:main', expect_success=False)
    self.Check(output, 'BUILD FAILED')

  def test_compile_fail(self):
    self.CreateFile('ATLAS', DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('main.cpp', INVALID_CPP_SOURCE)

    output = self.Run('build', 'out:main', expect_success=False)
    self.Check(output, 'BUILD FAILED')

  def test_mod_cpp_test(self):
    self.CreateFile('ATLAS', """
        CppTest(name = 'a_test',
                source = ['a_test.cpp'],
                library = ['util'])
        CppLibrary(name = 'util',
                   source = ['util.cpp'])
        """)

    # Don't use any 'real' testing frameworks to avoid dependencies.
    self.CreateFile('a_test.cpp',"""
        int main() {
	  return 0;
        }
        """)

    self.CreateFile('util.h', test_constants.UTIL_H_CONTENTS)
    self.CreateFile('util.cpp', test_constants.UTIL_CPP_CONTENTS)

    target_list = ['a_test', 'a_test.o']

    output = self.Run('test')
    self.CheckBuildFilesExist(target_list)
    self.Check(output, '1 TEST PASSED')

    output = self.Run('clean')
    self.CheckBuildFilesExist(target_list, exists=False)

  def test_crash_output(self):
    """Make sure that we capture stderr, stdout and hard crash message (system
       signal)."""
    self.CreateFile('ATLAS', """
        CppTest(name = 'main',
                source = ['main.cpp'])
        """)

    self.CreateFile('main.cpp',"""
        #include <iostream>
        using namespace std;
        int main() {
          cout << "I am stdout" << endl;
          cerr << "I am stderr" << endl;
          int * p = 0;
          *p = 1;
        }
        """)

    output = self.Run('test', expect_success=False)
    self.Check(output, 'I am stdout')
    self.Check(output, 'I am stderr')
    self.Check(output, 'Terminated: SIG.*')

  def test_build_cpp_depends(self):
    self.CreateFile('ATLAS', DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('header.h', '#include "out/header2.h"')
    self.CreateFile('header2.h', 'class C {};')
    self.CreateFile('main.cpp', """
        #include "out/header.h"
        int main() { return 0; }
        """)

    output = self.Run('build', flags=['-v'])
    self.Check(output, '(distcc|g\+\+).*main.o')

    future = os.stat('build/debug/out/main.o')[stat.ST_MTIME] + 1
    os.utime('out/header2.h', (future, future))

    output = self.Run('build', flags=['-v'])
    self.Check(output, '(distcc|g\+\+).*main.o')

  def test_missing_lib(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
                library = ['does_not_exist'])
        """)
    output = self.Run('build', flags=['--no-color'], expect_success=False)
    self.Check(output, 'Config Error: Missing reference: out:does_not_exist')

  def test_mod_lib(self):
    self.CreateFile('ATLAS', DEFAULT_ATLAS_LIB_CONTENTS)
    self.CreateFile('util.cpp', """
        bool IsEven(int a) { return (a % 2); }
        """)

    target_list = ['libutil.a', 'util.o']

    output = self.Run('build', 'out:util', flags=['-v'])
    self.Check(output, 'ar.*rcs.*util.o')
    self.CheckBuildFilesExist(target_list)

    self.Run('clean', 'out:util')
    self.CheckBuildFilesExist(target_list, exists=False)

  def test_mod_lib_fail(self):
    self.CreateFile('ATLAS', DEFAULT_ATLAS_LIB_CONTENTS)
    self.CreateFile('util.cpp', INVALID_CPP_SOURCE)

    output = self.Run('build', 'out:util', expect_success=False)
    self.Check(output, 'BUILD FAILED')

  def test_lib_depend_lib(self):
    self.CreateFile('ATLAS', """
                    CppExe(name = 'main',
                           source = ['main.cpp'],
                           library = ['one'])
                    CppLibrary(name = 'one',
                               source = ['one.cpp'],
                               library = ['two'])
                    CppLibrary(name = 'two',
                               source = ['two.cpp'],
                               library = ['three'])
                    CppLibrary(name = 'three',
                               source = ['three.cpp'])
                    """)
    self.CreateFile('main.cpp', """
        #include "out/one.h"
        #include "out/two.h"
        int main() { One(); Two(); }
        """)
    self.CreateFile('one.h', 'void One();')
    self.CreateFile('one.cpp', 'void One() {}')
    self.CreateFile('two.h', 'void Two();')
    self.CreateFile('two.cpp', """
                    #include "out/three.h"
                    void Two() { Three(); }
                    """)
    self.CreateFile('three.h', 'void Three();')
    self.CreateFile('three.cpp', 'void Three() {}')

    self.Run('build')

  def test_missing_source(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
                source = ['main.cpp'])
        """)

    output = self.Run('build', flags=['--no-color'], expect_success=False)
    self.Check(output, 'Config Error: Error opening CPP include file out/main.cpp')

  def test_circular_header_dep(self):
    self.CreateFile('ATLAS', DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('main.cpp', """
        #include "out/header.h"
        int main() { return 0; }
        """)

    self.CreateFile('header.h', """
        #ifndef HEADER_H__
        #define HEADER_H__
        #include "out/header.h"
        #include "out/header2.h"
        #endif
        """)

    self.CreateFile('header2.h', """
        #ifndef HEADER_2_H__
        #define HEADER_2_H__
        #include "out/header.h"
        #endif
        """)

    output = self.Run('build', 'out:main', flags=['--verbose'])
    self.CheckBuildFileExists('main')
    self.Check(output, 'Circular header dependency')


if __name__ == "__main__":
  atlas_test.main()
