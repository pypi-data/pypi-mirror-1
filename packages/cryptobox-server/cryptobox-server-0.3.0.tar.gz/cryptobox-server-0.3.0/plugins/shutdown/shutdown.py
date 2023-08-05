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

import cryptobox.plugins.base

REDIRECT_DELAY = 120

class shutdown(cryptobox.plugins.base.CryptoBoxPlugin):

	plugin_capabilities = [ "system" ]
	plugin_visibility = [ "menu" ]
	request_auth = False
	rank = 90

	def do_action(self, type=None):
		if not type:
			return "form_shutdown"
		elif type == "shutdown":
			if self.__do_shutdown("shutdown"):
				self.hdf["Data.Success"] = "Plugins.shutdown.Shutdown"
				return "progress_shutdown"
			else:
				self.hdf["Data.Warning"] = "Plugins.shutdown.ShutdownFailed"
				return "form_shutdown"
		elif type == "reboot":
			if self.__do_shutdown("reboot"):
				self.hdf["Data.Success"] = "Plugins.shutdown.Reboot"
				self.hdf["Data.Redirect.URL"] = "/"
				self.hdf["Data.Redirect.Delay"] = REDIRECT_DELAY
				return "progress_reboot"
			else:
				self.hdf["Data.Warning"] = "Plugins.shutdown.RebootFailed"
				return "form_shutdown"
		else:
			return "form_shutdown"


	def get_status(self):
		return "the box is up'n'running"


	def __do_shutdown(self, action):
		import subprocess
		import os
		proc = subprocess.Popen(
			shell = False,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"plugin",
				os.path.join(self.plugin_dir, "root_action.py"),
				action])
		proc.wait()
		return proc.returncode == 0

