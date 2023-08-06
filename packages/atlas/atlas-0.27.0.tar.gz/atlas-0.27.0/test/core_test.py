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
import commands
import os
import re

import atlas_test
import test_constants

from src import constants
from src import util


class CoreTest(atlas_test.TestCase):

  def CreateDefaultProject(self):
    self.CreateFile('ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)

  def test_run_command(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
               source = ['main.cpp'])
        """)

    self.CreateFile('main.cpp', """
        #include <cassert>
        #include <cstdio>
        #include <iostream>
        int main(int argc, const char ** argv) {
          std::cout << "I AM ALIVE";
          assert(argc == 3);
          assert( ! strcmp(argv[1], "--verbose"));
          assert( ! strcmp(argv[2], "true"));
          return 0;
        }
        """)

    output = self.Run('run', 'out:main', run_args=['--verbose', 'true'])
    self.Check(output, 'I AM ALIVE')

  def test_build_module(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main0',
                source = ['main0.cpp'])
        CppExe(name = 'main1',
                source = ['main1.cpp'])
        """)

    self.CreateFile('main0.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)
    self.CreateFile('main1.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)

    self.Run('build', 'out')
    self.CheckBuildFileExists('main0')
    self.CheckBuildFileExists('main1')

  def test_build_tree(self):
    # Test building entire subdirectory tree ('c').
    # a / b
    #   / c / d
    #       / e / f
    #
    for path in ['a', 'a/b', 'a/c', 'a/c/d', 'a/c/e', 'a/c/e/f']:
      self.CreateFile('%s/ATLAS' % path, test_constants.DEFAULT_ATLAS_CONTENTS)
      self.CreateFile('%s/main.cpp' % path, test_constants.DEFAULT_MAIN_CPP_CONTENTS)

    output = self.Run('build', 'out/a/c')
    self.CheckBuildFileExists('a/main', exists=False)
    self.CheckBuildFileExists('a/b/main', exists=False)
    self.CheckBuildFileExists('a/c/main')
    self.CheckBuildFileExists('a/c/d/main')
    self.CheckBuildFileExists('a/c/e/main')
    self.CheckBuildFileExists('a/c/e/f/main')

  def test_command_output_pipe(self):
    # Make sure that we properly handle buffered output. Originally had a bug that did not regularly flush stdout pipe for the test process, which ended up blocking the test and forcing a timeout.
    self.CreateFile('ATLAS', """
        CppTest(name = 'lots_of_output',
                source = ['main.cpp'])
        """)

    self.CreateFile('main.cpp', """
        #include <iostream>
        int main() {
          for (int i = 0; i < 10000; ++i) {
            std::cout << "LOTS AND LOTS OF OUTPUT";
          }
          return 0;
        }
        """)

    # If we handle output properly, this should exit correctly.
    self.Run('test', flags=['--test_timeout=10'])

  def test_command_output_capture(self):
    """Verify that stdout and stderr are captured from sub-command."""
    self.CreateFile('ATLAS', """
        CppTest(name = 'main',
                source = ['main.cpp'])
        """)

    self.CreateFile('main.cpp', """
        #include <iostream>
        int main() {
          std::cout << "STDOUT MESSAGE" << std::endl;
          std::cerr << "STDERR MESSAGE" << std::endl;
          return 1;  // fail so that we display show output
                     // TODO: add flag to print output anyway
        }
        """)

    # If we handle output properly, this should exit correctly.
    output = self.Run('test', expect_success=False);
    self.Check(output, 'STDOUT MESSAGE', True)
    self.Check(output, 'STDERR MESSAGE', True)

  def test_short_commands(self):
    """Test short version of all commands."""
    self.CreateFile('ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)

    for cmd in ['build', 'clean', 'test']:
      self.Run(cmd[:1])
      self.Run(cmd[:2])

    for cmd in ['rebuild', 'run',]:
      self.Run(cmd[:2])

  def test_all_targets(self):
    self.CreateFile('a/ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('b/ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)

    self.CreateFile('a/main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)
    self.CreateFile('b/main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)

    self.Run('build')
    self.CheckBuildFileExists('a/main')
    self.CheckBuildFileExists('b/main')

    self.Run('clean')
    self.CheckBuildFileExists('a/main', exists=False)
    self.CheckBuildFileExists('b/main', exists=False)

  def test_help(self):
    output = self.Run('build', flags=['--help'])
    self.Check(output, 'Usage:')

  def test_build_timeout(self):
    pass # TODO

  def test_test_timeout(self):
    TEST_NAME = 'atlas_core_test_timeout.py'
    self.CreateFile('ATLAS',"PythonTest('%s')" % TEST_NAME)
    self.CreateFile(TEST_NAME, """
        #!/usr/bin/python
        import unittest
        class Test(unittest.TestCase):
          def test(self):
            while(True): pass
        unittest.main()
        """)
    output = self.Run('test', flags=['--test_timeout=1', '-v'], expect_success=False)

    self.Check(output, 'TIMEOUT', True)
    # Verify subprocess is not running
    output = commands.getoutput('ps aux')
    self.assertFalse(TEST_NAME in output, "Found test process running on system... somehow we didn't propertly kill the child test process -- maybe you've been debugging and killed Atlas before it could properly kill child procs?")

  def test_clean_prune(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
                source = ['one/two/main.cpp'])
        """)
    self.CreateFile('one/two/main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)

    self.Run('build', 'out')
    self.CheckBuildFileExists('one/two/main.o')
    self.CheckBuildDirExists('one/two')
    self.CheckBuildDirExists('one')

    self.Run('clean', 'out')
    self.CheckBuildFileExists('one/two/main.o', exists=False)
    self.CheckBuildDirExists('one/two', exists=False)
    self.CheckBuildDirExists('one', exists=False)

  def test_serial(self):
    self.CreateDefaultProject()
    output = self.Run('build', 'out', flags=['--serial'])
    self.Check(output, 'Serial Mode')

  def test_parallel(self):
    self.CreateDefaultProject()
    output = self.Run('build', 'out', flags=['-v'])
    self.Check(output, 'Parallel Mode')

  def test_dependency_display(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
                source = ['main.cpp',
                          'util.cpp'])
        """)
    self.CreateFile('main.cpp', """
          #include "out/util.h"
          int main() { return 0; }
        """)
    self.CreateFile('util.cpp', """
          #include "out/util.h"
          I32 helper() {return 0;}
        """)
    self.CreateFile('types.h', 'typedef int I32;')
    self.CreateFile('util.h', """
          #include "out/types.h"
          I32 helper();
        """)
    self.Run('build')  # make sure valid CPP files
    output = self.Run('depend', 'out:main.cpp')
    self.Check(output, 'out:main.cpp has 2 dependencies')
    self.Check(output, 'out:types.h')
    self.Check(output, 'out:util.h')
    self.Check(output, 'out:util.cpp', False)

  def test_build_opt(self):
    self.CreateDefaultProject()
    self.Run('build', 'out', flags=['--opt'])
    self.CheckBuildFileExists('main', debug=False)

  def test_build_debug(self):
    self.CreateDefaultProject()
    output = self.Run('build', 'out', flags=['--verbose'])
    self.CheckBuildFileExists('main', debug=True)
    self.Check(output, '(distcc|g\+\+).* -g ')

  def test_build_fail(self):
    self.CreateFile('ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('main.cpp', 'THIS WILL NOT COMPILE!')
    output = self.Run('build', 'out', expect_success=False)
    self.Check(output, 'BUILD FAILED')

  def test_circular_dep(self):
    return  # TODO: Find scenario that could have a circular dependency
    self.CreateFile('ATLAS', """
        CppLibrary(name = 'main',
                   dep = ['util'])
        CppLibrary(name = 'util',
                   dep = ['main'])
        """)

    output = self.Run('build', 'out:main', flags=['--verbose'],
                      expect_success=False)
    self.Check(output, 'Circular dependency', True)

  def test_relative_module(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
               source = ['main.cpp'],
               library = ['util'])      # <--- We're testing this
        CppLibrary(name = 'util',
                   source = 'util.cpp')  # <--- Test scalar value
        """)
    self.CreateFile('main.cpp', test_constants.MAIN_WITH_UTIL_CPP_CONTENTS)
    self.CreateFile('util.h', test_constants.UTIL_H_CONTENTS)
    self.CreateFile('util.cpp', test_constants.UTIL_CPP_CONTENTS)

    self.Run('build')

  def test_one_of_many(self):
    # Make sure we properly handle the case where we only build 1 of multiple targets.
    self.CreateFile('one/ATLAS', """
        CppExe(name = 'main1',
                source = ['main1.cpp'])
        """)
    self.CreateFile('two/ATLAS', """
        CppExe(name = 'main2',
                source = ['main2.cpp'])
        """)
    self.CreateFile('one/main1.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)
    self.CreateFile('two/main2.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)

    self.Run('build', 'out/one:main1')

  def DISABLED_test_unknown_extension(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
                source = ['main.cpp'],
                unknown = ['dummy'])
        """)
    self.CreateFile('main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)
    self.assertRaises(util.ConfigError,
                      self.Run, 'build')

  def test_single_unittest(self):
    self.CreateFile('ATLAS',"PythonTest('test.py')")
    self.CreateFile('test.py', test_constants.DEFAULT_PY_TEST_CONTENTS)
    output = self.Run('test', 'out:test.py')
    self.Check(output, '1 TEST PASSED', True)

  def test_failing_tests(self):
    FAILING_PYTHON_TEST = """
        #!/usr/bin/python
        exit(1)
    """
    self.CreateFile('ATLAS',"""
        PythonTest('test1.py')
        PythonTest('test2.py')
        PythonTest('test3.py')
    """)
    self.CreateFile('test1.py', FAILING_PYTHON_TEST)
    self.CreateFile('test2.py', test_constants.DEFAULT_PY_TEST_CONTENTS)
    self.CreateFile('test3.py', FAILING_PYTHON_TEST)
    output = self.Run('test', flags=['--no-color', '--serial'], expect_success=False)
    self.Check(output, '2 TESTS FAILED')
    # Check for listing after "FAILED" (summary)
    self.Check(output, '2 TESTS FAILED\s+out:test[13].py\s+out:test[13].py\s+')

  def test_failing_test_limit_output(self):
    line_count = 1000
    FAILING_PYTHON_TEST = '\n'.join(["#!/usr/bin/python",
                                     "for i in range(%d):" % line_count,
                                     "  print 'some_test_output %s' % (i + 1)",
                                     "exit(1)"])
    self.CreateFile('ATLAS',"""
        PythonTest('test1.py')
    """)
    self.CreateFile('test1.py', FAILING_PYTHON_TEST)
    output = self.Run('test', expect_success=False)
    self.Check(output, '1 TEST FAILED')
    self.Check(output, 'some_test_output %s\s*$' % 1, False)
    self.Check(output, 'some_test_output %s\s*$' % (line_count - constants.MAX_TEST_OUTPUT_LINES), False)
    self.Check(output, 'some_test_output %s\s*$' % (line_count - constants.MAX_TEST_OUTPUT_LINES + 1))
    self.Check(output, 'some_test_output %s\s*$' % line_count)

  def test_option_color(self):
    self.CreateFile('ATLAS',"PythonTest('test.py')")
    self.CreateFile('test.py', test_constants.DEFAULT_PY_TEST_CONTENTS)

    # COLOR ENABLED
    output = self.Run('test', 'out:test.py')
    self.Check(output, '\033\[0.*1 TEST PASSED.*\033\[m', True)

    # NO COLOR
    output = self.Run('test', 'out:test.py', flags=['--no-color'])
    self.Check(output, '^\s*1 TEST PASSED\s*$', True)

  def test_temp_test_dir(self):
    # Verify that we give each test its own temp working directory
    self.CreateFile('ATLAS',"""
        PythonTest('test1.py')
        PythonTest('test2.py')
        """)
    self.CreateFile('test1.py', """
        #!/usr/bin/python
        import os
        assert not os.path.exists("test.out")
        open("test.out", "w").write("some text")
        """)
    self.CreateFile('test2.py', """
        #!/usr/bin/python
        import os
        import time
        time.sleep(1)
        assert not os.path.exists("test.out")
        """)

    # Run multiple times to make sure that we clean up after ourselves.
    for i in range(2):
      self.Run('test')

  def test_depend_param(self):
    self.CreateFile('ATLAS',"""
        CppExe('main',
               source = 'main.cpp')
        PythonTest('test.py',
                   depend = 'main')
        """)
    # TODO: Need better way to get project root dir within a test -- maybe a ENV var?
    self.CreateFile('test.py',"""
        #!/usr/bin/python
        import os
        import sys
        main_path = os.path.join(os.path.dirname(sys.argv[0]), '../build/debug/out/main.o')
        assert os.path.exists(main_path)
        """)
    self.CreateFile('main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)
    self.Run('test', 'out:test.py')

  def test_environment_vars(self):
    # Verify that we give each test its own temp working directory
    self.CreateFile('ATLAS',"""
        PythonTest('test.py')
        """)
    self.CreateFile('test.py', """
        #!/usr/bin/python
        import os
        assert os.environ['ATLAS_ROOT_DIR'] == '%s'
        assert os.environ['ATLAS_BUILD_DIR'] == '%s'
        """ % (os.getcwd(), os.path.join(os.getcwd(), 'build/debug'))
        )

    self.Run('test')

  def test_glob(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
               source = glob('*.cpp'))
        """)
    self.CreateFile('main.cpp', test_constants.MAIN_WITH_UTIL_CPP_CONTENTS)
    self.CreateFile('util.h', test_constants.UTIL_H_CONTENTS)
    self.CreateFile('util.cpp', test_constants.UTIL_CPP_CONTENTS)

    output = self.Run('build')
    self.CheckBuildFileExists('main.o')
    self.CheckBuildFileExists('util.o')

class IncludeTest(atlas_test.TestCase):

  def test_2_subdirs(self):
    self.CreateFile('ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('a/ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('b/ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('b/c/ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)

    self.CreateFile('main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)
    self.CreateFile('a/main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)
    self.CreateFile('b/main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)
    self.CreateFile('b/c/main.cpp', test_constants.DEFAULT_MAIN_CPP_CONTENTS)

    output = self.Run('build', 'out')
    output = self.Run('build', 'out/a')
    output = self.Run('build', 'out/b')
    output = self.Run('build', 'out/b/c')

    self.CheckBuildFileExists('main')
    self.CheckBuildFileExists('a/main')
    self.CheckBuildFileExists('b/c/main')

  def test_show_compiler_warnings(self):
    self.CreateFile('ATLAS', test_constants.DEFAULT_ATLAS_CONTENTS)
    self.CreateFile('main.cpp',"""
        #include <cstdio>
        int main() {
          int a;
          return 0;
        }
        """)

    output = self.Run('build')
    self.Check(output, 'warning: unused variable', True)

    # Second build won't show warning, since compile was successful (despite warnings)
    output = self.Run('build')
    self.Check(output, 'warning: unused variable', False)

    # TODO: Add flag to suppress build output
    #output = self.Run('rebuild', flags=['--hide_build_output')
    #self.Check(output, "warning: unknown escape sequence", False)


if __name__ == "__main__":
  atlas_test.main()
