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
# Tests for Flex SDK support
#
import time

import atlas_test


UTIL_AS_CONTENTS = """
    package {
      public class Util {
        public function ReturnTrue():Boolean {
          return true;
        }
      }
    }
    """

class FlexTest(atlas_test.TestCase):

  def test_build_app(self):
    self.CreateFile('ATLAS', """
        FlexApp(name = 'app',
                source = ['app.mxml'])
        """)

    self.CreateFile('app.mxml', """
        <?xml version="1.0" encoding="utf-8"?>
        <mx:Application xmlns:mx="http://www.adobe.com/2006/mxml" layout="absolute">
        </mx:Application>
        """)

    target_list = ['app.swf']
    output = self.Run('build')
    self.CheckBuildFilesExist(target_list)

    # Verify that we remove default output on success
    self.Check(output, '^Loading configuration file', False)

    self.Run('clean')
    self.CheckBuildFilesExist(target_list, exists=False)

  def test_data_depend(self):
    self.CreateFile('ATLAS', """
        FlexApp(name = 'app',
                source = ['app.mxml'],
                data = ['data1.txt',
                        'data2.txt'])
        """)

    self.CreateFile('app.mxml', """
        <?xml version="1.0" encoding="utf-8"?>
        <mx:Application xmlns:mx="http://www.adobe.com/2006/mxml" layout="absolute">
        </mx:Application>
        """)

    self.CreateFile('data1.txt', '')
    self.CreateFile('data2.txt', '')

    self.Run('build')

    time.sleep(1)

    self.CreateFile('data1.txt', '')  # Touch
    output = self.Run('build')

    self.Check(output, 'flex build.*out:app')

  def test_build_library(self):
    self.CreateFile('ATLAS', """
        FlexLibrary(name = 'util',
                    source = ['util.as'])
        """)

    self.CreateFile('util.as', UTIL_AS_CONTENTS)

    target_list = ['util.swc']
    self.Run('build')
    self.CheckBuildFilesExist(target_list)

    self.Run('clean')
    self.CheckBuildFilesExist(target_list, exists=False)

  def test_library_dependency(self):
    self.CreateFile('app/ATLAS', """
        FlexApp(name = 'app',
                source = 'app.mxml',
                library = '//out/util:util')
        """)
    self.CreateFile('util/ATLAS', """
        FlexLibrary(name = 'util',
                    source = ['util.as'])
        """)

    self.CreateFile('app/app.mxml', """
        <?xml version="1.0" encoding="utf-8"?>
        <mx:Application xmlns:mx="http://www.adobe.com/2006/mxml" layout="absolute"
         creationComplete="Init()">
         <mx:Script><![CDATA[
          public function Init():void {
            var u:Util = new Util();
            trace(u.ReturnTrue());
         }
         ]]></mx:Script>
        </mx:Application>
        """)

    self.CreateFile('util/util.as', UTIL_AS_CONTENTS)

    target_list = ['app/app.swf', 'util/util.swc']
    self.Run('build')
    self.CheckBuildFilesExist(target_list)

    self.Run('clean')
    self.CheckBuildFilesExist(target_list, exists=False)

  def DISABLED_test_test_app(self):
    """TODO"""
    self.CreateFile('ATLAS', """
        FlexTest(name = 'test',
                 source = ['test.as'])
        """)

    target_list = ['test.swf']

    output = self.Run('test')
    self.CheckBuildFilesExist(target_list)
    self.Check(output, '1 TEST PASSED')

    output = self.Run('clean')
    self.CheckBuildFilesExist(target_list, exists=False)


if __name__ == '__main__':
  atlas_test.main()
