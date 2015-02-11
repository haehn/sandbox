#!/usr/bin/env python
import os
import sys

import _zstack

def print_help( script_name ):
  '''
  '''
  description = ''
  print description
  print
  print 'Usage: ' + script_name + ' INPUT_DIRECTORY'
  print


#
# entry point
#
if __name__ == "__main__":

  # always show the help if no arguments were specified
  if len(sys.argv) != 0 and len( sys.argv ) < 2:
    print_help( sys.argv[0] )
    sys.exit( 1 )

  input_dir = sys.argv[1]

  manager = _zstack.Manager(input_dir)
  manager.start()

  webserver = _zstack.WebServer(manager)
  webserver.start()
  