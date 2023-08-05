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

"""Base class for all unittests involving the webserver.

This class uses twill.
"""

__revision__ = "$Id"

from cryptobox.tests.base import WebInterfaceTestClass



class WebServer(WebInterfaceTestClass):
	"""Basic tests for the webserver.
	"""

	def test_is_server_running(self):
		'''the server should run under given name and port'''
		self.register_auth(self.url)
		self.cmd.go(self.url)
		self.cmd.find("CBOX-STATUS")
		## other URLs must not be checked, as we do not know, if they are valid



class BuiltinPages(WebInterfaceTestClass):
	"""Basic test of builtin pages (no features).
	"""


	def test_goto_index(self):
		'''display all devices'''
		self.register_auth(self.url)
		self.cmd.go(self.url)
		self.cmd.find("The CryptoBox")
		self.cmd.go(self.url + "?weblang=de")
		self.cmd.find("Die CryptoBox")
		self.cmd.go(self.url + "?weblang=sl")
		self.cmd.find("Privatnost v vsako vas")
		self.cmd.go(self.url + "?weblang=fr")
		self.cmd.find("La CryptoBox")

