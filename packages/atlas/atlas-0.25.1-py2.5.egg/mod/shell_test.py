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
# shell_test.py - Run shell script tests.

import action
from globals import Define
from mod.file import FileComponent
from mod.test import TestComponent
import util


# ATLAS config interface
def ShellTest(name, **kwargs):
  Define(name, ShellTestComponent, **kwargs)


class ShellTestComponent(FileComponent, TestComponent):

  def Init(self, source, **kwargs):
    target = util.NameToPath(self.ConvertPaths(source)[0])
    FileComponent.Init(self, source=target, **kwargs)
    TestComponent.Init(self, target, **kwargs)
