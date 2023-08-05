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

from cryptobox.tests.base import WebInterfaceTestClass

class unittests(WebInterfaceTestClass):
	
	def test_get_cert_form(self):
		"""retrieve the default form of the certificate manager"""
		url = self.url + "encrypted_webinterface"
		self.register_auth(url)
		self.cmd.go(url)
		## TODO: enable it, as soon as the plugin is enabled by default
		#self.cmd.find("Data.Status.Plugins.encrypted_webinterface")

