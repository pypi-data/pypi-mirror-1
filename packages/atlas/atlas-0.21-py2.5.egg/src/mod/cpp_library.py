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
# Implements cpp_lib component.
#
import os

import action
from extension import Extension
import filecache
from globals import Define
from mod.cpp_binary import CppBinaryComponent
from registry import registry
import util


# ATLAS config interface
def CppLibrary(name, **kwargs):
  Define(name, CppLibraryComponent, **kwargs)


class LibExtension(Extension):
  def Depend(self, depend, reliant):
    reliant.AddLibrary(depend)
    for lib in depend.libs:
      reliant.AddLibrary(lib)
    for lib in depend.ext_libs:
      reliant.AddExternalLibrary(lib)
    

def Init():
  registry.RegisterExtension('library', 
                             CppBinaryComponent,
                             LibExtension(CppLibraryComponent,
                                          convert_paths=True))


class CppLibraryComponent(CppBinaryComponent):
  
  def Init(self, **kwargs):
    target = util.BuildPath(os.path.join(self.GetDirectory(),
                                         'lib%s.a' % self.GetShortName()))
    CppBinaryComponent.Init(self, target=target, **kwargs)

  def AddLibrary(self, comp):
    if not comp in self.libs:
      # Dependant libraries don't need to be built before reliant libraries. This greatly improves parallelism (takes 3/4 as long in my tests).
      self.libs.add(comp)
    
  def Build(self):
    util.MakeParentDir(self.target)
    filecache.Purge(self.target)

    cmd = action.BuildCommand('ar', 'build %s' % self.GetName())
    cmd.Add('rcs')
    cmd.AddPath(self.target)

    objects = list(self.objects)
    objects.sort(util.CompareName)  # Must sort names for non-deterministic results
    for o in objects:
      cmd.AddPath(o.GetTargetName())
  
    return cmd.Run()
