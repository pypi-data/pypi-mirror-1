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

IFCONFIG_BIN = "/sbin/ifconfig"
ROUTE_BIN = "/sbin/route"

import subprocess
import re
import sys

def __changeIP(interface, ipaddress, netmask="0"):
	__check_address(ipaddress)
	if netmask == "0":
		## change the IP only
		proc = subprocess.Popen(
			shell = False,
			args = [IFCONFIG_BIN, interface, ipaddress])
		proc.wait()
	else:
		## someone wants to change the netmask too
		__check_address(netmask)
		proc = subprocess.Popen(
			shell = False,
			args = [IFCONFIG_BIN, interface, ipaddress, "netmask", netmask])
		proc.wait()
	return proc.returncode == 0


def __changeGW(old_gw, new_gw):
	__check_address(old_gw)
	__check_address(new_gw)
	if old_gw != "0.0.0.0":
		## assume that a default route exists and delete it
		proc = subprocess.Popen(
			shell = False,
			args = [ROUTE_BIN, "del", "default", "gw", old_gw])
		proc.wait()
		## ignore errors
	proc = subprocess.Popen(
		shell = False,
		args = [ROUTE_BIN, "add", "default", "gw", new_gw])
	proc.wait()
	return proc.returncode == 0


def __check_address(address):
	"""Check for correct numbers in given address
	"""
	match = re.search(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', address)	
	## did we match? If yes, then: are there wrong values inside?
	if not match or [e for e in match.groups() if int(e) > 255]:
		sys.stderr.write("%s: illegal argument (%s)\n" % (self_bin, address))
		sys.exit(1)
	return


if __name__ == "__main__":
	args = sys.argv[1:]

	self_bin = sys.argv[0]
	
	if len(args) == 0:
		sys.stderr.write("%s: no argument supplied\n" % self_bin)
		sys.exit(1)
	
	try:
		if args[0] == "change_ip":
			if len(args) != 4: raise "InvalidArgNum"
			result = __changeIP(args[1], args[2], args[3])
		elif args[0] == "change_gw":
			if len(args) != 3: raise "InvalidArgNum"
			result = __changeGW(args[1], args[2])
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
	


