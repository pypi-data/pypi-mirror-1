#!/usr/bin/env python
#
# Copyright 2006 sense.lab e.V.
# 
# This file is part of the CryptoBox.
#
# The CryptoBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# The CryptoBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the CryptoBox; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

__revision__ = "$Id"


## necessary: otherwise CryptoBoxRootActions.py will refuse to execute this script
PLUGIN_TYPE = "cryptobox"

SHUTDOWN_BIN = "/sbin/shutdown"

## delay (in seconds) before shutdown
SHUTDOWN_DELAY = 3

import subprocess
import sys


def call_prog(progy):
	proc = subprocess.Popen(
	shell = False,
		args = progy)
	proc.communicate()
	return proc.returncode == 0


if __name__ == "__main__":
	args = sys.argv[1:]

	self_bin = sys.argv[0]
	
	if len(args) > 1:
		sys.stderr.write("%s: too many arguments (%s)\n" % (self_bin, args))
		sys.exit(1)
	
	if len(args) == 0:
		sys.stderr.write("%s: no argument supplied\n" % self_bin)
		sys.exit(1)
	
	if args[0] == "reboot":
		result = call_prog([SHUTDOWN_BIN, "-t", str(SHUTDOWN_DELAY), "-r", "now"])
	elif args[0] == "shutdown":
		result = call_prog([SHUTDOWN_BIN, "-t", str(SHUTDOWN_DELAY), "-h", "now"])
	else:
		sys.stderr.write("%s: illegal argument (%s)\n" % (self_bin, args[0]))
		sys.exit(1)
	
	if result:
		sys.exit(0)
	else:
		sys.exit(1)

