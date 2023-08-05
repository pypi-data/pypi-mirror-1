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

SFDISK_BIN = "/sbin/sfdisk"
MKFS_BIN = "/sbin/mkfs"
LABEL_BIN = "/sbin/e2label"

import subprocess
import re
import sys
import os


def __partitionDevice(device):
	## do not use the "-q" flag, as this spoils the exit code of sfdisk (seems to be a bug)
	proc = subprocess.Popen(
		shell	= False,
		args	= [
			SFDISK_BIN,
			"-uM",
			device])
	proc.wait()
	return proc.returncode == 0


def __formatPartition(device, type):
	import time, threading
	result = True
	def formatting():
		proc = subprocess.Popen(
			shell	= False,
			stdin	= subprocess.PIPE,
			stdout	= subprocess.PIPE,
			stderr	= subprocess.PIPE,
			args	= [
				MKFS_BIN,
				"-t", type,
				device])
		proc.wait()
		## TODO: very ugly way of communication: it assumes, that failures are fast - success is slow
		if proc.returncode == 0:
			time.sleep(1)
			return True
		else:
			return False
	thread = threading.Thread()
	thread.setDaemon(True)
	thread.run = formatting
	thread.start()
	time.sleep(0.5)
	return thread.isAlive()


def __labelPartition(device, label):
	proc = subprocess.Popen(
		shell	= False,
		args	= [
			LABEL_BIN,
			device,
			label])
	proc.wait()
	return proc.returncode == 0


if __name__ == "__main__":
	args = sys.argv[1:]

	self_bin =sys.argv[0]
	
	if len(args) == 0:
		sys.stderr.write("%s: no argument supplied\n" % self_bin)
		sys.exit(1)

	try:
		if args[0] == "partition":
			if len(args) != 2: raise "InvalidArgNum"
			result = __partitionDevice(args[1])
		elif args[0] == "format":
			if len(args) != 3: raise "InvalidArgNum"
			result = __formatPartition(args[1], args[2])
		elif args[0] == "label":
			if len(args) != 3: raise "InvalidArgNum"
			result = __labelPartition(args[1], args[2])
		else:
			sys.stderr.write("%s: invalid action (%s)\n" % (self_bin, args[0]))
			sys.exit(1)
		if result:
			sys.exit(0)
		else:
			sys.exit(1)
	except "InvalidArgNum":
		sys.stderr.write("%s: invalid number of arguments (%s)\n" % (self_bin, args))
		sys.exit(1)
	
