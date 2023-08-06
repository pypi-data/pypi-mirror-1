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
# Atlas - A simple, extendible, all-purpose build system
#
import getopt
import os
import sys

import action
import constants
import filecache
from flags import flags
import globals
from graph import Graph
import loader
import log
import metrics
from registry import registry
import util


def usage(error=None):
  if error:
    print 'Error: ', error
  print """Usage: atlas [options] [command] [targets]

Commands:
   build            compile/generate output files
   test             build and run all tests
   clean            delete all intermediate build files

   display          (debug) print dependency layout
   rebuild          (debug) clean + build

Options:
    --no-color      turn off colored text output
    --opt           build 'opt' (release) configuration. (default is 'debug')
    --serial        run jobs in sequence, not parallel.
    -v, --verbose   output extra info

    --metrics       (debug) print system call information

    --test_timeout  Timeout (in sec) for individual tests.
"""

def Main(args):

  metrics.total_timer.Start()
  print "Atlas v%s" % constants.VERSION

  flags.__init__()
  filecache.Init()
  registry.__init__()


  opts, args = getopt.getopt(
      args,
      'v', 
      ['test_timeout=', 'help', 'metrics', 'no-color', 'opt', 'serial', 'verbose',
       'version'])

  for o, a in opts:
    if o in ['--help']:
      usage()
      return True
    elif o in ['--metrics']:
      flags.metrics = True
    elif o in ['--no-color']:
      flags.color = False
    elif o in ['--opt']:
      flags.debug = False
    elif o in ['--serial']:
      flags.parallel = False
    elif o in ['--test_timeout']:
      constants.TEST_TIMEOUT = int(a)  # TODO: Modifying 'constants' is messy
      log.Info("Test timeout set to %d secs" % constants.TEST_TIMEOUT)
    elif o in ['-v', '--verbose']:
      print "[Verbose Mode]"
      flags.verbose = True
    elif o in ['--version']:
      return True  # Version printed above

  if not args:
    usage()
    return False

  command = args[0]
  targets = args[1:]

  command_map = {
                 'display': Graph.Display,
                 'clean': Graph.Clean,
                 'build': Graph.Build,
                 'rebuild': Graph.Rebuild,
                 'test': Graph.Test
                }

  if command not in command_map:
    usage('Unknown command: ' + command)
    return False

  deps = Graph()
  globals.master_graph = deps  # Need a better way to set module-wide global
  success = None 
  try:
    metrics.load_timer.Start()
    deps = Graph()
    parser = loader.Loader(deps)
    globals.master_loader = parser  # Need a better way to set module-wide global
    parser.Load(os.getcwd())
    metrics.load_timer.Stop()

    metrics.action_timer.Start()
    success = command_map[command](deps, targets)
    metrics.action_timer.Stop()

    metrics.total_timer.Stop()
    metrics.Report(command, targets)
    return success

  except util.ConfigError, e:
    print 'Config Error: %s' % e
    raise
    return False
  except action.CommandError, e:
    print 'Command Error: %s' % e
    return False


if __name__ == '__main__':
  success = Main(sys.argv[1:])
  if success:
    exit(0)
  else:
    exit(1)
