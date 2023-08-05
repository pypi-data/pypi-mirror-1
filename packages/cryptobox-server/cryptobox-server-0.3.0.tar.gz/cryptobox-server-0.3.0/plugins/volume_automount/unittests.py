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
		"""try to read automount form"""
		url = self.url + "volume_automount?weblang=en&device=" + self.device_html
		self.register_auth(url)
		## first: turn it off
		self.cmd.go(url + "&action=disable")
		self.cmd.go(url)
		self.cmd.find('is disabled')


	def test_toggle(self):
		"""try to toggle automount property"""
		url = self.url + "volume_automount"
		self.register_auth(url)
		self.cmd.go(url + "?device=%s&action=disable" % self.device_html)
		self.cmd.find("Automatic activation disabled")
		self.cmd.find("is disabled")
		self.cmd.go(url + "?device=%s&action=enable" % self.device_html)
		self.cmd.find("Automatic activation enabled")
		self.cmd.find("is enabled")
		

	def test_invalid_input(self):
		"""check invalid inputs"""
		url = self.url + "volume_automount"
		self.register_auth(url)
		self.cmd.go(url + "?device=%s&action=foobar" % self.device_html)
		self.cmd.notfind("Automatic activation disabled")
		self.cmd.notfind("Automatic activation enabled")
		
