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
import os

import constants
import log
import metrics
from registry import registry
import util


class Component(object):

  def __init__(self, name, **kwargs):
    self.name = name
    self.depends = set()
    self.reliants = set()
    self.kwargs = kwargs
    self.defined = False  # True when defined by a config file
    self.constructed = False  # True when 'Init' has been called.
    metrics.total_components += 1

  def __str__(self):
    return self.DisplayName()

  def Build(self):
    pass  # Default: no action

  def Test(self):
    pass # Default: no action

  def Clean(self):
    pass  # Default: no action

  def AddDepend(self, comp):
    assert comp
    if self.HasReliant(comp):
      raise util.ConfigError(
          "Circular dependency detected. %s is already reliant on %s"
          % (comp, self))

    self.depends.add(comp)
    comp.reliants.add(self)

  def HasReliant(self, comp):
    #print "HasReliant(%s) for %s" % (path, self.GetPath())
    path = util.RelPath(comp.GetPath())
    if self.GetPath() == path:
      return True
    # TODO: Cache all reliants for each component to avoid recursion
    for rel in self.reliants:
      if rel.HasReliant(comp):
        return True
    return False

  def SetDefined(self):
    self.defined = True

  def IsDefined(self):
    return self.defined

  def GetPath(self):
    return self.name.replace(':', '/')

  def GetName(self):
    return self.name

  def GetShortName(self):
    if ':' in self.name:
      pos = self.name.find(':') + 1
      return self.name[pos:]
    else:
      return self.name

  def DisplayName(self):
    return self.GetName()

  def GetDirectory(self):
    return os.path.dirname(self.GetPath())

  def GetRecursiveModifyTime(self):
    # TODO: This goes away when i re-work how components/targets/outputs work
    if self.depends:
      youngest = max([d.GetRecursiveModifyTime() for d in self.depends])
      return max(youngest, self.GetModifyTime())
    else:
      return self.GetModifyTime()

  def Init(self, depend=None, **kwargs):
    # TODO: Move this to a 'depend' extension?
    if depend:
      for d in self.ConvertPaths(depend):
        self.AddDepend(registry.Reference(d))

  def OnInit(self):
    timer = metrics.Timer()
    timer.Start(resume=True)

    if not self.constructed:
      if not self.IsDefined():
        raise util.ConfigError('Component %s is not defined in an ATLAS file' % self)
      self.constructed = True
      #print "Init: %s" % self
      try:
        self.Init(**self.kwargs)
      except util.ConfigError, e:
        print "Defining %s" % self
        raise

      metrics.total_components_init += 1

    timer.Stop()
    metrics.analysis_timer.Add(timer)

  def OnBuild(self):
    assert self.constructed
    youngest = constants.MAX_AGE
    if self.depends:
      youngest = max([d.GetRecursiveModifyTime() for d in self.depends])
    if self.NeedsBuild(youngest):
      # 'Clean' so that old version doesn't exist on build failure
      self.OnClean()  # TODO: Check failure
      return self.Build()
    else:
      return None

  def OnClean(self):
    assert self.constructed
    return self.Clean()

  def OnTest(self):
    assert self.constructed
    return self.Test()

  def OnDisplay(self, indent=''):
    assert self.constructed
    print '%s%s' % (indent, self.GetName())
    for depend in self.depends:
      depend.OnDisplay(indent + '  ')
    return True

  def ProcessExtensions(self, map):
    # Process Extensions First (may modify include_dirs)
    for key, values in map.items():
      ext = registry.GetExtension(key, type(self))
      if ext:
        if ext.convert_paths:
          values = self.ConvertPaths(values)
        for v in values:
          comp = registry.Reference(v, ext.comp_type)
          comp.OnInit()
          #log.Info('Processing extension %s for comp %s' % (key, comp))
          ext.Depend(comp, self)
      else:
        raise util.ConfigError('Unrecognized extension "%s" for %s'
                               % (key, self))

  def ConvertPaths(self, paths):
    # Paths can be scalar string or a list of strings. We always return a list.
    results = util.ConvertPaths(paths, self.GetDirectory())
    if isinstance(results, list):
      return results
    else:
      return [results]
