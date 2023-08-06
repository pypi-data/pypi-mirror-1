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
# atlas_test.py - Testing utilities
#
import os
import commands
import re
import shutil
import stat
import StringIO
import sys
import time
import unittest

import test_constants

sys.path.append('..')
import atlas_main
import util


class TestCase(unittest.TestCase):

  def setUp(self):
    shutil.rmtree('out', ignore_errors=True)
    shutil.rmtree('build', ignore_errors=True)

  def Run(self, action, targets=None, expect_success=True, flags=None, run_args=None):
    args = []
    if flags:
      args.extend(flags)
    args.append(action)
    if targets:
      if isinstance(targets, list):
        args.extend(targets)
      else:
        args.append(targets)
    if run_args:
      args.extend(run_args)

    output = StringIO.StringIO()
    sys.stdout = output
    sys.stderr = output

    success = atlas_main.Main(args)

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    if expect_success != success:
      print '-' * 50
      print output.getvalue()
      print '-' * 50
      self.fail('Command succeeded: %s. Expected %s.' % (success, expect_success))
    return output.getvalue()

  def CreateFile(self, name, contents):
    # Clean up whitespace
    contents = re.sub('^\s*\n', '', contents)  # Remove inital newline
    m = re.match('^(\s*)', contents)
    if m:
      index = len(m.group(0))
      p = re.compile('^' + m.group(0), re.MULTILINE)
      contents = p.sub('', contents)
    # Write file
    path = os.path.join(test_constants.TEST_DIR, name)
    util.MakeDir(os.path.dirname(path))
    file = open(path, 'w')
    file.write(contents + '\n')
    file.close()

  def Check(self, output, pattern, result=True):
    p = re.compile(pattern, re.MULTILINE)
    if result != (p.search(output) is not None):
      print
      print '-' * 50
      print output
      print '-' * 50
      self.fail()

  def GetBuildPath(self, name, debug=True):
    if debug:
      dir = 'debug'
    else:
      dir = 'opt'
    return os.path.join('build', dir, 'out', name)

  def CheckBuildDirExists(self, name, exists=True, debug=True):
    path = self.GetBuildPath(name, debug)
    if exists != os.path.exists(path) or (exists and not os.path.isdir(path)):
      self.fail('Directory exists (%s) check failed: %s' % (exists, path))

  def CheckBuildFileExists(self, name, exists=True, debug=True):
    path = self.GetBuildPath(name, debug)
    if exists != os.path.exists(path) or (exists and os.path.isdir(path)):
      self.fail('File exists (%s) check failed: %s' % (exists, path))

  def CheckBuildFilesExist(self, names, exists=True, debug=True):
    for name in names:
      self.CheckBuildFileExists(name, exists, debug)

  def GetModifyTime(self, tilename):
    return os.stat(filename)[stat.ST_MTIME]

  def SetModifyTime(self, filename, mod_time):
    assert util.Exists(filename)
    os.utime(filename, (mod_time, mod_time))

  def Touch(self, filename):
    now = time.time()
    self.SetModifyTime(filename, now)


def main():
  unittest.main()
