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

from cryptobox.tests.base import WebInterfaceTestClass

class unittests(WebInterfaceTestClass):

	def test_read_form(self):
		self.cmd.go(self.url + "system_preferences")
		self.cmd.find("Preferences")


	def test_check_plugins(self):
		self.cmd.go(self.url + "system_preferences")
		self.cmd.find(r'Data.Status.Plugins.system_preferences=(.*)$', "m")
		plugins = self.locals["__match__"].split(":")
		self.assertTrue(len(plugins) > 1)
		self.assertTrue("disks" in plugins)

