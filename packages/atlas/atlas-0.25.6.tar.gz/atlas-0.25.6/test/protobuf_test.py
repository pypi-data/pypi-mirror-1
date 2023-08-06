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
# Tests for Google Rrotocol Buffer extension
#
import os
import stat
import time

import atlas_test


TEST_PB_CONTENTS = """
    message Deposit {
      required string name = 1;
      required int32 amount = 2;
    }
"""

TEST_MAIN_CPP_CONTENTS = """
    #include "out/deposit.pb.h"
    int main() {
      Deposit d;
      d.set_name("mike");
    }
"""

UTIL_CPP_CONTENTS = """
    void util_func() {}
"""

class ModuleTest(atlas_test.TestCase):

  def test_mod_protobuf(self):
    self.CreateFile('ATLAS',"ProtocolBuffer('deposit.proto')")
    self.CreateFile('deposit.proto', TEST_PB_CONTENTS)

    self.Run('build', 'out')
    self.CheckBuildFilesExist(['deposit.pb.h',
                               'deposit.pb.cc',
                               'deposit_pb2.py'])

    self.Run('clean', 'out')
    self.CheckBuildFilesExist(['deposit.pb.h',
                               'deposit.pb.cc',
                               'deposit_pb2.py'],
                              exists=False)

  def test_cpp_exe_depend(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
               source = ['main.cpp'],
               protobuf = ['deposit.proto'])
        ProtocolBuffer('deposit.proto')
        """)

    self.CreateFile('deposit.proto', TEST_PB_CONTENTS)
    self.CreateFile('main.cpp', TEST_MAIN_CPP_CONTENTS)

    self.Run('build')
    self.CheckBuildFilesExist(['deposit.pb.h',
                               'deposit.pb.cc',
                               'deposit.pb.o',
                               'main.o',
                               'main'])

    self.Run('clean')
    self.CheckBuildFilesExist(['deposit.pb.h',
                               'deposit.pb.cc',
                               'deposit.pb.o',
                               'main.o',
                               'main'],
                              exists=False)

  def test_cpp_exe_depend_subdir(self):
    # TODO: I'm having a failing test with a/b/c/pb.h
    self.CreateFile('a/b/ATLAS', """
        CppExe(name = 'main',
               source = ['main.cpp'],
               protobuf = ['deposit.proto'])
        ProtocolBuffer('deposit.proto')
        """)

    self.CreateFile('a/b/deposit.proto', TEST_PB_CONTENTS)
    self.CreateFile('a/b/main.cpp', """
        #include "out/a/b/header.h"
        int main() {
          Deposit d;
        }
    """)
    self.CreateFile('a/b/header.h', """
        #include "out/a/b/deposit.pb.h"
    """)

    self.Run('build')

  def test_cpp_lib_relative(self):
    self.CreateFile('ATLAS', """
        CppExe(name = 'main',
               source = ['main.cpp'],
               library = ['util:util'])
        """)
    self.CreateFile('util/ATLAS', """
        CppLibrary(name = 'util',
                   source = 'util.cpp',
                   protobuf = ['deposit.proto'])
        ProtocolBuffer('deposit.proto')
        """)
    self.CreateFile('main.cpp',"""
        #include "out/util/deposit.pb.h"
        int main() {
          Deposit d;
          d.set_name("mike");
         }
         """)
    self.CreateFile('util/util.cpp', UTIL_CPP_CONTENTS)
    self.CreateFile('util/deposit.proto', TEST_PB_CONTENTS)
    self.Run('build')

  def test_cpp_lib_absolute(self):
    self.CreateFile('main/ATLAS', """
        CppExe(name = 'main',
               source = ['main.cpp'],
               library = ['//out/util:util'])
        """)
    self.CreateFile('util/ATLAS', """
        CppLibrary(name = 'util',
                   source = 'util.cpp',
                   protobuf = ['deposit.proto'])
        ProtocolBuffer('deposit.proto')
        """)
    self.CreateFile('main/main.cpp',"""
        #include "out/util/deposit.pb.h"
        int main() {
          Deposit d;
          d.set_name("mike");
         }
         """)
    self.CreateFile('util/util.cpp', UTIL_CPP_CONTENTS)
    self.CreateFile('util/deposit.proto', TEST_PB_CONTENTS)
    self.Run('build')


  def test_proto_import(self):
    self.CreateFile('ATLAS',"""
        CppExe(name = 'main',
               source = 'main.cpp',
               protobuf = 'circle.proto')
        ProtocolBuffer('point.proto')
        ProtocolBuffer('scale.proto')
        ProtocolBuffer('circle.proto')
        """)
    self.CreateFile('main.cpp', """
        #include "out/circle.pb.h"
        int main() {
          Circle c;
          c.mutable_point()->set_x(0);
        }
        """)
    self.CreateFile('point.proto', """
        message Point {
          required float x = 1;
          required float y = 2;
        }
        """)
    self.CreateFile('scale.proto', """
        message Scale {
          required float value = 1;
        }
        """)
    self.CreateFile('circle.proto', """
        import "out/scale.proto";   // absolute path
        // TODO: Have Atlas allow relative paths (seem to confuse protoc compiler)
        //import "point.proto";    // relative path
        import "out/point.proto";
        message Circle {
          required Point point = 1;
          required Scale scale = 2;
        }
        """)

    output = self.Run('build', flags=['-v'])
    self.Check(output, 'protoc.*point.proto')
    self.Check(output, 'protoc.*circle.proto')
    self.Check(output, '(distcc|g\+\+).*main')

    # Change direct CPP dependency
    time.sleep(1)
    self.Touch('out/circle.proto')

    output = self.Run('build', flags=['-v'])
    self.Check(output, 'protoc.*point.proto', False)
    self.Check(output, 'protoc.*circle.proto')
    self.Check(output, '(distcc|g\+\+).*main.o')

    # Change nested dependency
    time.sleep(1)
    self.Touch('out/point.proto')

    output = self.Run('build', flags=['-v'])
    self.Check(output, 'protoc.*point.proto')
    self.Check(output, 'protoc.*circle.proto')
    self.Check(output, '(distcc|g\+\+).*main.o')

    # No changes
    output = self.Run('build', flags=['-v'])
    self.Check(output, 'protoc.*point.proto', False)
    self.Check(output, 'protoc.*circle.proto', False)
    self.Check(output, '(distcc|g\+\+).*main.o', False)


if __name__ == "__main__":
  atlas_test.main()
