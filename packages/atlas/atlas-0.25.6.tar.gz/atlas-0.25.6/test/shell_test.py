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
# Tests for Shell script support
#
#
import time

import atlas_test


class ShellTest(atlas_test.TestCase):

  def test_shell_builder(self):
    self.CreateFile('ATLAS', """
        ShellBuilder('gen_out.sh',
                     input = ['in.txt'],
                     output = ['out.txt'])
        """)
    self.CreateFile('gen_out.sh', """
        #!/bin/bash
        cp $ATLAS_ROOT_DIR/out/in.txt $ATLAS_BUILD_DIR/out/out.txt
        """)
    # TODO:  $ATLAS_OUT_FILE
    self.CreateFile('in.txt', 'some source data')

    output = self.Run('build')
    self.Check(output, 'gen_out.sh')
    self.CheckBuildFileExists('out.txt')

    output = self.Run('build')
    self.Check(output, 'gen_out.sh', False)

    self.Touch('out/in.txt')
    time.sleep(1)

    output = self.Run('build')
    self.Check(output, 'gen_out.sh')

    output = self.Run('clean', flags=['--verbose'])
    self.CheckBuildFileExists('out.txt', False)

  def test_shell_test(self):
    self.CreateFile('ATLAS', """
        ShellTest(name = 'passing',
                source = 'test_pass.sh')
        ShellTest(name = 'failing',
                source = 'test_fail.sh')
        """)
    self.CreateFile('test_pass.sh', """
        #!/bin/bash
        echo Hello
        """)
    self.CreateFile('test_fail.sh', """
        #!/bin/bash
        ! echo Hello
        """)

    output = self.Run('test', 'out:passing', flags=['--no-color'])
    self.Check(output, 'PASS\s+out:passing')
    self.Check(output, '1 TEST PASSED')

    output = self.Run('test', 'out:failing', expect_success=False)
    self.Check(output, '1 TEST FAILED')


if __name__ == '__main__':
  atlas_test.main()
