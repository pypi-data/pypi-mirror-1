#!/usr/bin/env python
#
# Copyright 2007 sense.lab e.V.
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

STUNNEL_BIN = "/usr/bin/stunnel4"

import sys
import os


def _get_username():
	if ("SUPERCMD" in os.environ) and ("ORIG_USER" in os.environ):
		return os.environ["ORIG_USER"]
	elif "USER" in os.environ:
		return os.environ["USER"]
	else:
		return "cryptobox"


def run_stunnel(cert_file, src_port, dst_port, pid_file):
	import subprocess
	if not src_port.isdigit():
		sys.stderr.write("Source port is not a number: %s" % src_port)
		return False
	if not dst_port.isdigit():
		sys.stderr.write("Destination port is not a number: %s" % dst_port)
		return False
	if not os.path.isfile(cert_file):
		sys.stderr.write("The certificate file (%s) does not exist!" % cert_file)
		return False
	username = _get_username()
	if not username:
		sys.stderr.write("Could not retrieve the username with uid=%d." % os.getuid())
		return False
	## the environment (especially PATH) should be clean, as 'stunnel' cares about
	## this in a setuid situation
	proc = subprocess.Popen(
		shell = False,
		env = {},
		stdin = subprocess.PIPE,
		args = [ STUNNEL_BIN,
			"-fd",
			"0"])
	proc.stdin.write("setuid = %s\n" % username)
	proc.stdin.write("pid = %s\n" % pid_file)
	proc.stdin.write("[cryptobox-server]\n")
	proc.stdin.write("connect = %s\n" % src_port)
	proc.stdin.write("accept = %s\n" % dst_port)
	proc.stdin.write("cert = %s\n" % cert_file)
	(output, error) = proc.communicate()
	return proc.returncode == 0
	

if __name__ == "__main__":
	args = sys.argv[1:]

	self_bin = sys.argv[0]
	
	if len(args) != 4:
		sys.stderr.write("%s: invalid number of arguments (%d instead of %d))\n" % \
				(self_bin, len(args), 4))
		sys.exit(1)
	
	if not run_stunnel(args[0], args[1], args[2], args[3]):
		sys.stderr.write("%s: failed to run 'stunnel'!" % self_bin)
		sys.exit(100)
	
	sys.exit(0)

